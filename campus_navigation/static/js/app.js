(() => {
    "use strict";

    const state = {
        data: null,
        mapGraph: null,
        rooms: new Map(),
        points: new Map(),
        viewer: null,
        selectedRoom: null,
        currentPoint: null,
        route: null,
        socket: null,
        reconnectTimer: null,
        shareToken: null,
        cameraStream: null,
        scanTimer: null,
        view: document.body.dataset.initialView === "2d" ? "2d" : "3d",
    };

    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => [...document.querySelectorAll(selector)];
    const svgNS = "http://www.w3.org/2000/svg";

    document.addEventListener("DOMContentLoaded", initialize);

    async function initialize() {
        bindStaticControls();
        try {
            const [mapGraph, campusData] = await Promise.all([
                loadGroundFloorMap(),
                loadCampusData(),
            ]);
            state.mapGraph = mapGraph;
            state.data = campusData;
            state.rooms = new Map(state.data.rooms.map((room) => [room.room_code, room]));
            state.points = new Map(state.data.navigation_points.map((point) => [point.code, point]));
            if (!state.data.rooms.length) throw new Error("No campus rooms are loaded. Run: python manage.py seed_gwcet");

            populateControls();
            draw2DMap();
            let threeDSuccess = false;
            try {
                buildScene();
                threeDSuccess = true;
            } catch (err3d) {
                console.warn("3D scene initialization error, falling back to 2D view:", err3d);
                toast("3D scene unavailable; operating in 2D floorplan mode.", true);
            }
            setCurrentPoint(state.points.get("MAIN_GATE"));
            setView(threeDSuccess ? state.view : "2d");
            connectWebSocket();
            $("#loading-screen").classList.add("done");
        } catch (error) {
            console.error(error);
            showInitializationError(error);
        }
    }

    async function loadGroundFloorMap() {
        if (!window.campusNavigator?.ready) {
            throw new Error("The campus navigator could not be initialized.");
        }

        try {
            return await window.campusNavigator.ready;
        } catch (error) {
            throw new Error(`Unable to load the ground-floor map. ${error.message}`);
        }
    }

    async function loadCampusData() {
        const response = await fetch("/api/bootstrap/");
        if (!response.ok) throw new Error("Campus API is unavailable.");
        return response.json();
    }

    function buildScene() {
        if (!window.THREE || !window.GWCET3DViewer) {
            throw new Error("The 3D library could not load. Check the internet connection or use the 2D view.");
        }
        state.viewer = new window.GWCET3DViewer($("#three-view"), (code) => selectRoom(code));
        state.viewer.buildCampus(state.data);
    }

    function showInitializationError(error) {
        const message = error instanceof Error ? error.message : "The campus map could not be loaded.";
        const loadingScreen = $("#loading-screen");
        loadingScreen.classList.add("error");
        loadingScreen.setAttribute("role", "alert");
        $("#loading-screen strong").textContent = "Unable to load the campus map";
        $("#loading-screen small").textContent = message;
        if (!$("#error-dismiss-btn")) {
            const btn = document.createElement("button");
            btn.id = "error-dismiss-btn";
            btn.type = "button";
            btn.className = "primary-button";
            btn.style.marginTop = "14px";
            btn.textContent = "Dismiss & Open Map";
            btn.onclick = () => loadingScreen.classList.add("done");
            loadingScreen.appendChild(btn);
        }
        toast(message, true);
    }

    function bindStaticControls() {
        $("#room-search").addEventListener("input", (event) => renderSearch(event.target.value));
        $("#room-search").addEventListener("focus", (event) => {
            if (event.target.value.trim()) renderSearch(event.target.value);
        });
        document.addEventListener("click", (event) => {
            if (!event.target.closest(".search-section")) $("#search-results").hidden = true;
        });
        document.addEventListener("keydown", (event) => {
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
                event.preventDefault();
                $("#room-search").focus();
            }
            if (event.key === "Escape") $("#search-results").hidden = true;
        });

        $$(".quick-filters button").forEach((button) => button.addEventListener("click", () => {
            const wasActive = button.classList.contains("active");
            $$(".quick-filters button").forEach((item) => item.classList.remove("active"));
            if (!wasActive) button.classList.add("active");
            renderSearch($("#room-search").value, wasActive ? "" : button.dataset.category);
        }));

        $("#start-location").addEventListener("change", (event) => setCurrentPoint(state.points.get(event.target.value)));
        $("#destination").addEventListener("change", (event) => {
            if (event.target.value) selectRoom(event.target.value, false);
        });
        $("#navigate-btn").addEventListener("click", calculateRoute);
        $("#room-navigate-button").addEventListener("click", () => {
            if (!state.selectedRoom) return;
            $("#destination").value = state.selectedRoom.room_code;
            calculateRoute();
        });
        $("#room-view-button").addEventListener("click", () => {
            if (!state.selectedRoom) return;
            setView("3d");
            state.viewer.focusRoom(state.selectedRoom.room_code);
        });
        $("#close-room-sheet").addEventListener("click", () => { $("#room-sheet").hidden = true; });
        $("#close-route").addEventListener("click", clearRoute);
        $("#clear-destination").addEventListener("click", () => {
            $("#destination").value = "";
            clearRoute();
        });
        $("#swap-route").addEventListener("click", swapRoute);
        $("#simulate-route").addEventListener("click", simulateRoute);

        $$("[data-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
        $$("[data-floor]").forEach((button) => button.addEventListener("click", () => setFloor(button.dataset.floor)));
        $("#reset-camera").addEventListener("click", () => state.viewer?.resetCamera());
        $("#toggle-labels").addEventListener("click", (event) => {
            const visible = state.viewer?.toggleLabels();
            $$(".svg-label").forEach((label) => { label.style.display = visible ? "" : "none"; });
            event.currentTarget.classList.toggle("active", visible);
        });

        $("#scan-qr-btn").addEventListener("click", () => $("#qr-dialog").showModal());
        $("#apply-qr").addEventListener("click", applySelectedQR);
        $("#start-camera").addEventListener("click", startCameraScanner);
        $("#qr-dialog").addEventListener("close", stopCameraScanner);

        $("#open-share-btn").addEventListener("click", () => $("#share-dialog").showModal());
        $$("[data-share-tab]").forEach((button) => button.addEventListener("click", () => switchShareTab(button.dataset.shareTab)));
        $("#start-sharing").addEventListener("click", startSharing);
        $("#stop-sharing").addEventListener("click", stopSharing);
        $("#join-sharing").addEventListener("click", joinSharing);
    }

    function populateControls() {
        const start = $("#start-location");
        const destination = $("#destination");
        const qrSelect = $("#qr-location-select");
        start.innerHTML = "";
        destination.innerHTML = '<option value="">Choose a destination</option>';
        qrSelect.innerHTML = "";

        const pointPriority = { GATE: 0, ENTRANCE: 1, CORRIDOR: 2, COURTYARD: 3, STAIR: 4, ROOM_DOOR: 5 };
        [...state.data.navigation_points]
            .sort((a, b) => (pointPriority[a.point_type] ?? 9) - (pointPriority[b.point_type] ?? 9) || a.name.localeCompare(b.name))
            .forEach((point) => start.add(new Option(`${point.name} · ${floorName(point.floor_level)}`, point.code)));

        state.data.rooms.filter((room) => room.is_active).forEach((room) => {
            destination.add(new Option(`${room.name} · ${room.floor_name}`, room.room_code));
        });
        state.data.qr_locations.forEach((qr) => qrSelect.add(new Option(qr.label, qr.code)));
        start.value = "MAIN_GATE";
        destination.value = "GF_LIBRARY";
        $("#room-count").textContent = state.data.rooms.length;
        $("#qr-count").textContent = state.data.qr_locations.length;
    }

    function renderSearch(query = "", category = "") {
        const normalized = query.trim().toLowerCase();
        const results = state.data?.rooms.filter((room) => {
            const haystack = `${room.name} ${room.room_code} ${room.aliases} ${room.category} ${room.department || ""}`.toLowerCase();
            return room.is_active && (!normalized || haystack.includes(normalized)) && (!category || room.room_type === category);
        }).slice(0, 12) || [];

        const panel = $("#search-results");
        panel.innerHTML = "";
        if (!results.length) {
            const empty = document.createElement("div");
            empty.className = "empty-result";
            empty.textContent = "No matching campus place found.";
            panel.appendChild(empty);
        } else {
            results.forEach((room) => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "result-item";
                button.innerHTML = `<span class="result-icon">${categoryIcon(room.room_type)}</span><span><strong>${escapeHTML(room.name)}</strong><small>${escapeHTML(room.floor_name)} · ${escapeHTML(room.wing)} · ${escapeHTML(room.category)}</small></span><b>›</b>`;
                button.addEventListener("click", () => {
                    selectRoom(room.room_code, true);
                    panel.hidden = true;
                    $("#room-search").value = room.name;
                });
                panel.appendChild(button);
            });
        }
        panel.hidden = false;
    }

    function selectRoom(code, focus = false) {
        const room = state.rooms.get(code);
        if (!room) return;
        state.selectedRoom = room;
        state.viewer?.selectRoom(code, focus);
        highlight2DRoom(code);
        $("#room-meta").textContent = `${room.room_code} · ${room.floor_name} · ${room.wing} wing`;
        $("#room-title").textContent = room.name;
        $("#room-description").textContent = room.closure_note || room.description;
        $("#room-category-icon").textContent = categoryIcon(room.room_type);
        $("#room-sheet").hidden = false;
    }

    async function calculateRoute() {
        const start = $("#start-location").value;
        const destination = $("#destination").value;
        if (!start || !destination) {
            toast("Choose both your current location and destination.", true);
            return;
        }
        const button = $("#navigate-btn");
        button.disabled = true;
        button.querySelector("span").textContent = "Calculating…";
        try {
            const response = await fetch("/api/route/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ start, destination, accessible: $("#accessible-route").checked }),
            });
            const payload = await response.json();
            if (!response.ok) throw new Error(payload.detail || "Route calculation failed.");
            showRoute(payload);
        } catch (error) {
            toast(error.message, true);
        } finally {
            button.disabled = false;
            button.querySelector("span").textContent = "Start navigation";
        }
    }

    function showRoute(route) {
        state.route = route;
        state.viewer?.drawRoute(route.points);
        draw2DRoute(route.points);
        const destinationRoom = state.rooms.get($("#destination").value);
        $("#route-title").textContent = destinationRoom ? `To ${destinationRoom.name}` : "Your route";
        $("#route-distance").textContent = `${route.distance_metres} m`;
        $("#route-time").textContent = `${route.estimated_minutes} min`;
        $("#route-floor").textContent = "G";
        $("#route-estimate").textContent = `${route.distance_metres} m · ${route.estimated_minutes} min`;
        const steps = $("#route-steps");
        steps.innerHTML = "";
        compactInstructions(route.instructions).forEach((instruction) => {
            const item = document.createElement("li");
            item.textContent = instruction;
            steps.appendChild(item);
        });
        $("#route-panel").hidden = false;
        $("#room-sheet").hidden = true;
        toast(`Shortest route found: ${route.distance_metres} metres.`);
    }

    function clearRoute() {
        state.route = null;
        state.viewer?.clearRoute();
        $("#svg-route").setAttribute("points", "");
        $("#svg-destination-marker").setAttribute("visibility", "hidden");
        $("#route-panel").hidden = true;
        $("#route-estimate").textContent = "Ready";
    }

    function swapRoute() {
        const destinationRoom = state.rooms.get($("#destination").value);
        if (!destinationRoom?.navigation_point) {
            toast("Choose a destination before swapping.");
            return;
        }
        const previousStart = $("#start-location").value;
        const roomAtOldStart = state.data.rooms.find((room) => room.navigation_point === previousStart);
        if (!roomAtOldStart?.is_active) {
            toast("The current location is not available as a room destination, so this route cannot be swapped.", true);
            return;
        }
        $("#start-location").value = destinationRoom.navigation_point;
        $("#destination").value = roomAtOldStart.room_code;
        setCurrentPoint(state.points.get(destinationRoom.navigation_point));
        clearRoute();
    }

    async function simulateRoute() {
        if (!state.route) return;
        const button = $("#simulate-route");
        button.disabled = true;
        button.textContent = "Walking…";
        for (const point of state.route.points) {
            setCurrentPoint(point, false);
            await delay(420);
        }
        const finalPoint = state.route.points[state.route.points.length - 1];
        if ([...$("#start-location").options].some((option) => option.value === finalPoint.code)) {
            $("#start-location").value = finalPoint.code;
        }
        button.disabled = false;
        button.textContent = "✓ Walk complete";
        setTimeout(() => { button.textContent = "▶ Simulate walk"; }, 1700);
        toast("You have arrived at your destination.");
    }

    function setCurrentPoint(point, updateSelect = true) {
        if (!point) return;
        state.currentPoint = point;
        state.viewer?.setCurrentLocation(point);
        update2DMarker("#svg-current-marker", point);
        if (updateSelect && [...$("#start-location").options].some((option) => option.value === point.code)) {
            $("#start-location").value = point.code;
        }
        broadcastPosition();
    }

    function setView(view) {
        state.view = view;
        $("#three-view").classList.toggle("active", view === "3d");
        $("#two-view").classList.toggle("active", view === "2d");
        $$("[data-view]").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
        if (view === "3d") setTimeout(() => state.viewer?.resize(), 30);
    }

    function setFloor(level) {
        $$("[data-floor]").forEach((button) => button.classList.toggle("active", button.dataset.floor === level));
        state.viewer?.setFloor(level);
        const label = level === "all" ? "All Floors · Concept Stack" : `${floorName(Number(level))} · Main Building`;
        $("#floor-context").textContent = label;
        if (level !== "0" && level !== "all") {
            setView("3d");
            toast(`${floorName(Number(level))} shell shown. Exact room layout is waiting for survey data.`);
        }
    }

    function draw2DMap() {
        const svg = $("#floorplan-svg");
        svg.innerHTML = "";
        addSVG(svg, "rect", { x: -72, y: -70, width: 144, height: 150, rx: 3, class: "svg-site" });
        addSVG(svg, "rect", { x: -70, y: 39, width: 55, height: 32, rx: 2, fill: "#84918f", opacity: ".8" });
        addSVG(svg, "text", { x: -42, y: 56, class: "svg-label" }, "PARKING");
        addSVG(svg, "rect", { x: 22, y: 37, width: 48, height: 34, rx: 2, fill: "#b59f68", opacity: ".9" });
        addSVG(svg, "text", { x: 46, y: 55, class: "svg-label" }, "PLAYGROUND");
        addSVG(svg, "rect", { x: -4.5, y: 37, width: 9, height: 28, fill: "#ded9c7" });
        addSVG(svg, "text", { x: 0, y: 68, class: "svg-label small" }, "MAIN GATE");
        addSVG(svg, "rect", { x: -43, y: -38, width: 94, height: 70, rx: 1.5, class: "svg-building" });
        addSVG(svg, "rect", { x: -15.5, y: -15.5, width: 31, height: 31, rx: 1, class: "svg-courtyard" });

        state.data.edges.forEach((edge) => {
            const start = state.points.get(edge.start);
            const end = state.points.get(edge.end);
            if (!start || !end || start.point_type === "ROOM_DOOR" || end.point_type === "ROOM_DOOR") return;
            addSVG(svg, "line", { x1: start.x, y1: -start.y, x2: end.x, y2: -end.y, class: "svg-corridor" });
        });

        state.data.rooms.filter((room) => room.floor_level === 0).forEach((room) => {
            if (room.room_code === "GF_COURTYARD") return;
            const rect = addSVG(svg, "rect", {
                x: room.x - room.width / 2,
                y: -room.y - room.length / 2,
                width: room.width,
                height: room.length,
                rx: .65,
                class: `svg-room ${room.room_type}`,
                "data-room-code": room.room_code,
                tabindex: "0",
            });
            rect.addEventListener("click", () => selectRoom(room.room_code));
            rect.addEventListener("keydown", (event) => { if (event.key === "Enter") selectRoom(room.room_code); });
            const label = room.name.replace("Laboratory", "Lab").replace("Classroom", "Class").replace("Reception / Enquiry", "Reception");
            addSVG(svg, "text", { x: room.x, y: -room.y + .7, class: `svg-label ${label.length > 16 ? "small" : ""}` }, label.length > 20 ? room.room_code.replace("GF_", "") : label);
        });

        addSVG(svg, "polyline", { id: "svg-route", class: "svg-route", points: "" });
        addSVG(svg, "circle", { id: "svg-current-marker", class: "svg-marker-current", cx: 0, cy: 62, r: 1.7 });
        addSVG(svg, "circle", { id: "svg-destination-marker", class: "svg-marker-destination", cx: 0, cy: 0, r: 1.7, visibility: "hidden" });
        addSVG(svg, "circle", { id: "svg-shared-marker", class: "svg-marker-shared", cx: 0, cy: 0, r: 1.7, visibility: "hidden" });
    }

    function draw2DRoute(points) {
        $("#svg-route").setAttribute("points", points.map((point) => `${point.x},${-point.y}`).join(" "));
        const last = points[points.length - 1];
        update2DMarker("#svg-destination-marker", last);
    }

    function highlight2DRoom(code) {
        $$(".svg-room").forEach((room) => room.classList.toggle("selected", room.dataset.roomCode === code));
    }

    function update2DMarker(selector, point) {
        const marker = $(selector);
        if (!marker || !point) return;
        marker.setAttribute("cx", point.x);
        marker.setAttribute("cy", -point.y);
        marker.setAttribute("visibility", "visible");
    }

    function addSVG(parent, tag, attributes, text = "") {
        const node = document.createElementNS(svgNS, tag);
        Object.entries(attributes).forEach(([name, value]) => node.setAttribute(name, value));
        if (text) node.textContent = text;
        parent.appendChild(node);
        return node;
    }

    function applySelectedQR() {
        const qr = state.data.qr_locations.find((item) => item.code === $("#qr-location-select").value);
        if (!qr) return;
        applyQRPoint(qr.navigation_point, qr.label);
        $("#qr-dialog").close();
    }

    function applyQRPoint(pointCode, label) {
        const point = state.points.get(pointCode);
        if (!point) {
            toast("This QR marker is not part of the current campus map.", true);
            return;
        }
        setCurrentPoint(point);
        toast(`Current location set to ${label || point.name}.`);
    }

    async function startCameraScanner() {
        if (!("BarcodeDetector" in window) || !navigator.mediaDevices?.getUserMedia) {
            toast("Live QR scanning is not supported in this browser. Choose a campus anchor below.", true);
            return;
        }
        try {
            const detector = new BarcodeDetector({ formats: ["qr_code"] });
            state.cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            const video = $("#qr-video");
            video.srcObject = state.cameraStream;
            video.hidden = false;
            await video.play();
            $("#start-camera").hidden = true;
            const scan = async () => {
                if (!state.cameraStream) return;
                const codes = await detector.detect(video).catch(() => []);
                if (codes.length) {
                    const raw = codes[0].rawValue;
                    let pointCode = raw;
                    try {
                        const payload = JSON.parse(raw);
                        pointCode = payload.point || payload.code;
                    } catch (_) {
                        const qr = state.data.qr_locations.find((item) => item.code === raw);
                        if (qr) pointCode = qr.navigation_point;
                    }
                    applyQRPoint(pointCode, "scanned QR marker");
                    $("#qr-dialog").close();
                    return;
                }
                state.scanTimer = requestAnimationFrame(scan);
            };
            scan();
        } catch (error) {
            toast("Camera access was not available. You can still choose a demo anchor.", true);
        }
    }

    function stopCameraScanner() {
        if (state.scanTimer) cancelAnimationFrame(state.scanTimer);
        if (state.cameraStream) state.cameraStream.getTracks().forEach((track) => track.stop());
        state.cameraStream = null;
        $("#qr-video").hidden = true;
        $("#start-camera").hidden = false;
    }

    function connectWebSocket() {
        if ([WebSocket.CONNECTING, WebSocket.OPEN].includes(state.socket?.readyState)) return;
        clearTimeout(state.reconnectTimer);
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socket = new WebSocket(`${protocol}://${window.location.host}/ws/tracker/`);
        state.socket = socket;
        socket.addEventListener("open", () => {
            clearTimeout(state.reconnectTimer);
            setSocketStatus(true);
        });
        socket.addEventListener("message", (event) => {
            try {
                handleSocketMessage(JSON.parse(event.data));
            } catch (error) {
                console.warn("Ignored an invalid live-tracking message.", error);
                toast("A malformed live-tracking update was ignored.", true);
            }
        });
        socket.addEventListener("close", () => {
            if (state.socket === socket) state.socket = null;
            setSocketStatus(false);
            clearTimeout(state.reconnectTimer);
            state.reconnectTimer = setTimeout(connectWebSocket, 3500);
        });
    }

    function setSocketStatus(connected) {
        const status = $("#socket-status");
        status.classList.toggle("offline", !connected);
        status.lastChild.textContent = connected ? " Private live ready" : " Reconnecting";
    }

    function socketSend(payload) {
        if (state.socket?.readyState !== WebSocket.OPEN) {
            toast("Live tracking is reconnecting. Try again in a moment.", true);
            return false;
        }
        state.socket.send(JSON.stringify(payload));
        return true;
    }

    function startSharing() {
        if (!$("#share-consent").checked) {
            toast("Tick the consent box before starting a location share.", true);
            return;
        }
        socketSend({
            action: "start_share",
            consent: true,
            display_name: $("#share-name").value,
            duration: Number($("#share-duration").value),
        });
    }

    function stopSharing() {
        if (socketSend({ action: "stop_share" })) state.shareToken = null;
    }

    function joinSharing() {
        const token = $("#join-code").value.trim().toUpperCase();
        if (token.length !== 6) {
            toast("Enter the six-character private share code.", true);
            return;
        }
        socketSend({ action: "join_share", token });
    }

    function handleSocketMessage(data) {
        if (data.event === "share_started") {
            state.shareToken = data.token;
            $("#share-active").hidden = false;
            $("#share-code").textContent = data.token;
            $("#share-expiry").textContent = `Expires ${new Date(data.expires_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
            $("#start-sharing").hidden = true;
            broadcastPosition();
            toast("Private location share started.");
        } else if (data.event === "share_stopped" || data.event === "share_ended") {
            state.shareToken = null;
            $("#share-active").hidden = true;
            $("#start-sharing").hidden = false;
            state.viewer?.hideSharedLocation();
            $("#svg-shared-marker").setAttribute("visibility", "hidden");
            if (data.reason) toast(data.reason);
        } else if (data.event === "share_joined") {
            $("#follow-status").textContent = `Following ${data.display_name}. Waiting for their next position update…`;
            toast(`Approved share connected for ${data.display_name}.`);
        } else if (data.event === "position_update") {
            state.viewer?.setSharedLocation(data);
            update2DMarker("#svg-shared-marker", data);
            $("#follow-status").textContent = `${data.display_name}: ${data.room_name || data.point_code} · updated ${new Date(data.updated_at).toLocaleTimeString()}`;
        } else if (data.event === "error") {
            toast(data.message, true);
        }
    }

    function broadcastPosition() {
        if (!state.shareToken || !state.currentPoint || state.socket?.readyState !== WebSocket.OPEN) return;
        socketSend({
            action: "position_update",
            point_code: state.currentPoint.code,
            room_name: state.currentPoint.name,
            floor: state.currentPoint.floor_level,
            x: state.currentPoint.x,
            y: state.currentPoint.y,
            z: state.currentPoint.z,
        });
    }

    function switchShareTab(tab) {
        $$("[data-share-tab]").forEach((button) => button.classList.toggle("active", button.dataset.shareTab === tab));
        $("#share-tab").hidden = tab !== "share";
        $("#join-tab").hidden = tab !== "join";
    }

    function compactInstructions(items) {
        return items.filter((item, index) => index === 0 || index === items.length - 1 || item !== items[index - 1]);
    }

    function categoryIcon(category) {
        return {
            ADMINISTRATION: "◇", CLASSROOM: "▦", LABORATORY: "⌬", LIBRARY: "▤",
            STAFF_ROOM: "◎", WASHROOM: "◒", STAIRCASE: "⌁", ENTRANCE: "↥",
            SERVICE_COUNTER: "◈", OTHER: "⌂",
        }[category] || "⌂";
    }

    function floorName(level) {
        return ["Ground Floor", "First Floor", "Second Floor"][level] || `Floor ${level}`;
    }

    function escapeHTML(value) {
        const div = document.createElement("div");
        div.textContent = value || "";
        return div.innerHTML;
    }

    function delay(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

    let toastTimer;
    function toast(message, isError = false) {
        const element = $("#toast");
        element.textContent = message;
        element.classList.toggle("error", isError);
        element.classList.add("show");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => element.classList.remove("show"), 3300);
    }
})();
