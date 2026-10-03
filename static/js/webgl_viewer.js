/* global THREE */

class GWCET3DViewer {
    constructor(container, onRoomSelect) {
        this.container = container;
        this.onRoomSelect = onRoomSelect;
        this.roomMeshes = new Map();
        this.labels = [];
        this.selectables = [];
        this.selectedCode = null;
        this.routeObject = null;
        this.routeMaterial = null;
        this.currentMarker = null;
        this.destinationMarker = null;
        this.sharedMarker = null;
        this.labelsVisible = true;
        this.clock = new THREE.Clock();
        this.init();
    }

    init() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xa9c5d1);
        this.scene.fog = new THREE.FogExp2(0xa9c5d1, 0.0018);

        this.camera = new THREE.PerspectiveCamera(42, 1, 0.1, 700);
        this.camera.position.set(82, 84, 108);

        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "high-performance" });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = .72;
        this.container.appendChild(this.renderer.domElement);

        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.065;
        this.controls.minDistance = 28;
        this.controls.maxDistance = 240;
        this.controls.maxPolarAngle = Math.PI * 0.48;
        this.controls.target.set(0, 0, 0);

        this.scene.add(new THREE.HemisphereLight(0xe8f4f7, 0x53624d, .72));
        const sun = new THREE.DirectionalLight(0xfff0d2, 1.15);
        sun.position.set(-45, 95, 65);
        sun.castShadow = true;
        sun.shadow.mapSize.set(2048, 2048);
        sun.shadow.camera.left = -110;
        sun.shadow.camera.right = 110;
        sun.shadow.camera.top = 110;
        sun.shadow.camera.bottom = -110;
        sun.shadow.bias = -.00025;
        this.scene.add(sun);

        const fill = new THREE.DirectionalLight(0xb9d5e5, .22);
        fill.position.set(65, 38, -70);
        this.scene.add(fill);

        this.raycaster = new THREE.Raycaster();
        this.pointer = new THREE.Vector2();
        this.renderer.domElement.addEventListener("pointerdown", (event) => this.pickRoom(event));
        this.renderer.domElement.addEventListener("pointermove", (event) => this.hoverRoom(event));
        this.resizeObserver = new ResizeObserver(() => this.resize());
        this.resizeObserver.observe(this.container);
        this.resize();
        this.animate();
    }

    buildCampus(data) {
        this.data = data;
        this.pointsByCode = new Map(data.navigation_points.map((point) => [point.code, point]));
        this.siteGroup = new THREE.Group();
        this.siteGroup.name = "SITE";
        this.groundFloorGroup = new THREE.Group();
        this.groundFloorGroup.name = "GROUND_FLOOR";
        this.floorGroups = new Map();
        this.floorGroups.set(0, this.groundFloorGroup);

        data.floors.forEach((floor) => {
            if (floor.level > 0) {
                const group = new THREE.Group();
                group.name = `FLOOR_${floor.level}`;
                this.floorGroups.set(floor.level, group);
                this.scene.add(group);
            }
        });

        this.scene.add(this.siteGroup, this.groundFloorGroup);

        this.buildSite();
        this.buildGroundSlab();
        this.buildUpperFloorDecks(data.floors);
        this.buildCorridors(data);
        data.rooms.forEach((room) => this.buildRoom(room));
        this.buildMarkers();
        this.setCurrentLocation(this.pointsByCode.get("MAIN_GATE"));
    }

    makeBox(width, height, depth, color, x, y, z, options = {}) {
        const material = new THREE.MeshStandardMaterial({
            color,
            roughness: options.roughness ?? 0.72,
            metalness: options.metalness ?? 0.02,
            transparent: Boolean(options.transparent),
            opacity: options.opacity ?? 1,
        });
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
        mesh.position.set(x, y, z);
        mesh.castShadow = options.castShadow !== false;
        mesh.receiveShadow = options.receiveShadow !== false;
        return mesh;
    }

    buildSite() {
        const lawn = this.makeBox(180, 0.6, 175, 0x708d63, 0, -0.5, 8, { castShadow: false, roughness: 1 });
        lawn.name = "CAMPUS_GROUND";
        this.siteGroup.add(lawn);

        const path = this.makeBox(9, 0.22, 33, 0xbeb9aa, 0, -0.08, 49, { castShadow: false, roughness: .96 });
        this.siteGroup.add(path);
        const pathLine = this.makeBox(0.28, 0.03, 33, 0xeee6c7, 0, 0.06, 49, { castShadow: false });
        this.siteGroup.add(pathLine);

        const parking = this.makeBox(58, 0.18, 34, 0x4d5557, -45, -0.12, 52, { castShadow: false, roughness: 1 });
        this.siteGroup.add(parking);
        for (let index = 0; index < 5; index += 1) {
            const line = this.makeBox(0.18, 0.03, 10, 0xf1ead2, -67 + index * 11, 0, 52, { castShadow: false });
            this.siteGroup.add(line);
            if (index < 4) {
                const car = this.makeBox(6.8, 1.3, 3.2, [0x274f63, 0xa84735, 0xd7d8d2, 0x4c5257][index], -61.5 + index * 11, 0.72, 52, { roughness: .38, metalness: .28 });
                car.rotation.y = Math.PI / 2;
                this.siteGroup.add(car);
            }
        }

        const playground = this.makeBox(54, 0.16, 38, 0xa7925d, 51, -0.11, 51, { castShadow: false, roughness: 1 });
        this.siteGroup.add(playground);
        const court = this.makeBox(26, 0.08, 16, 0xa9573f, 43, 0.01, 50, { castShadow: false, roughness: .88 });
        this.siteGroup.add(court);
        [31, 55].forEach((x) => this.siteGroup.add(this.makeBox(0.16, 0.04, 16, 0xf3e9d0, x, .07, 50, { castShadow: false })));
        this.siteGroup.add(this.makeBox(26, .04, .16, 0xf3e9d0, 43, .07, 50, { castShadow: false }));
        this.siteGroup.add(this.makeBox(.16, .04, 16, 0xf3e9d0, 43, .07, 50, { castShadow: false }));

        const gateMaterial = 0x293a3d;
        this.siteGroup.add(this.makeBox(1.7, 5.5, 1.7, gateMaterial, -6, 2.5, 62));
        this.siteGroup.add(this.makeBox(1.7, 5.5, 1.7, gateMaterial, 6, 2.5, 62));
        this.siteGroup.add(this.makeBox(13.5, 1.2, 1.4, gateMaterial, 0, 5.1, 62));
        const gateLabel = this.makeLabel("MAIN GATE", 0xffffff, 11);
        gateLabel.position.set(0, 6.1, 61.2);
        this.siteGroup.add(gateLabel);

        [-73, -58, 69].forEach((x, idx) => {
            for (let z = 33 + idx * 2; z <= 70; z += 14) this.addTree(x, z, this.siteGroup, .9);
        });
    }

    buildGroundSlab() {
        const slabColor = 0xa69e8f;
        const slabs = [
            this.makeBox(84, .55, 15, slabColor, 0, .08, 31),
            this.makeBox(84, .55, 17, slabColor, 0, .08, -31),
            this.makeBox(18, .55, 47, slabColor, -33, .08, 0),
            this.makeBox(18, .55, 47, slabColor, 33, .08, 0),
        ];
        slabs.forEach((slab) => this.groundFloorGroup.add(slab));

        const courtyard = this.makeBox(31, .22, 31, 0x608f52, 0, .18, 0, { castShadow: false, roughness: 1 });
        courtyard.userData.roomCode = "GF_COURTYARD";
        courtyard.userData.baseColor = courtyard.material.color.getHex();
        courtyard.name = "GF_COURTYARD";
        this.roomMeshes.set("GF_COURTYARD", courtyard);
        this.selectables.push(courtyard);
        this.groundFloorGroup.add(courtyard);
        this.groundFloorGroup.add(this.makeBox(3.2, .05, 31, 0xc9c0a9, 0, .33, 0, { castShadow: false }));
        this.groundFloorGroup.add(this.makeBox(31, .05, 3.2, 0xc9c0a9, 0, .34, 0, { castShadow: false }));
        [[-9,-9],[9,-9],[-9,9],[9,9]].forEach(([x,z]) => this.addTree(x, z, this.groundFloorGroup, .68));
        [-7, 7].forEach((x) => {
            const bench = this.makeBox(4.5, .35, .8, 0x8b5c3d, x, .7, -6, { roughness: .9 });
            this.groundFloorGroup.add(bench);
        });
    }

    buildCorridors(data) {
        data.edges.forEach((edge) => {
            const start = this.pointsByCode.get(edge.start);
            const end = this.pointsByCode.get(edge.end);
            if (!start || !end || start.floor_level !== end.floor_level) return;
            if (start.point_type === "ROOM_DOOR" || end.point_type === "ROOM_DOOR") return;
            const floorLevel = start.floor_level;
            const targetGroup = this.floorGroups.get(floorLevel);
            if (!targetGroup) return;
            const elevation = start.z ?? floorLevel * 3.66;
            const x1 = start.x;
            const z1 = -start.y;
            const x2 = end.x;
            const z2 = -end.y;
            const length = Math.hypot(x2 - x1, z2 - z1);
            const corridor = this.makeBox(3.2, .12, length + .2, 0xb4aa94, (x1 + x2) / 2, elevation + .42, (z1 + z2) / 2, { castShadow: false, roughness: .94 });
            corridor.rotation.y = Math.atan2(x2 - x1, z2 - z1);
            targetGroup.add(corridor);
        });
    }

    buildRoom(room) {
        if (["GF_COURTYARD", "FF_COURTYARD", "SF_COURTYARD"].includes(room.room_code)) return;
        const colors = {
            ADMINISTRATION: 0xb87335,
            CLASSROOM: 0xc5a05f,
            LABORATORY: 0x4f7b88,
            LIBRARY: 0x8d4936,
            STAFF_ROOM: 0xa96043,
            WASHROOM: 0x4d8078,
            STAIRCASE: 0x5c6666,
            ENTRANCE: 0x4f7854,
            SERVICE_COUNTER: 0xb9793f,
            OTHER: 0x7e7950,
        };
        const height = room.room_type === "ENTRANCE" ? 1.4 : 2.65;
        const color = colors[room.room_type] || 0x958565;
        const floorElev = room.z !== undefined ? room.z : (room.floor_level * 3.66);
        const targetGroup = this.floorGroups.get(room.floor_level) || this.groundFloorGroup;

        const mesh = this.makeBox(room.width - .35, height, room.length - .35, color, room.x, floorElev + height / 2 + .4, -room.y, { roughness: .82 });
        mesh.name = room.model_object_name || room.room_code;
        mesh.userData.roomCode = room.room_code;
        mesh.userData.baseColor = color;

        const outline = new THREE.LineSegments(
            new THREE.EdgesGeometry(mesh.geometry),
            new THREE.LineBasicMaterial({ color: 0x403e38, transparent: true, opacity: .48 })
        );
        mesh.add(outline);
        targetGroup.add(mesh);
        this.roomMeshes.set(room.room_code, mesh);
        this.selectables.push(mesh);
        
        this.addBuildingFinish(room, height, color, floorElev, targetGroup);

        const important = room.room_type !== "CLASSROOM" || ["GF_CLASS_L1", "SF_CLASS_01", "SF_LAB_01"].includes(room.room_code);
        if (important) {
            const label = this.makeLabel(this.shortLabel(room.name));
            label.position.set(room.x, floorElev + height + 2.15, -room.y);
            label.userData.floorLevel = room.floor_level;
            this.labels.push(label);
            targetGroup.add(label);
        }

        if (room.navigation_point) {
            const point = this.pointsByCode.get(room.navigation_point);
            if (point) {
                const door = this.makeBox(.95, 1.15, .22, 0x334548, point.x, floorElev + 1.0, -point.y, { castShadow: false, roughness: .48, metalness: .08 });
                targetGroup.add(door);
            }
        }
    }

    addBuildingFinish(room, height, wallColor, floorElev, targetGroup) {
        const width = room.width - .35;
        const depth = room.length - .35;
        const roofColor = new THREE.Color(wallColor).offsetHSL(0, -.08, -.18).getHex();
        const roof = this.makeBox(width + .12, .16, depth + .12, roofColor, room.x, floorElev + height + .48, -room.y, {
            roughness: .94,
            castShadow: false,
        });
        targetGroup.add(roof);

        if (["WASHROOM", "STAIRCASE"].includes(room.room_type)) return;

        const glassColor = room.room_type === "ENTRANCE" ? 0x496f74 : 0x59757a;
        const windowHeight = Math.min(.62, height * .32);
        const windowY = floorElev + .4 + height * .58;
        const windowOptions = {
            transparent: true,
            opacity: .82,
            roughness: .22,
            metalness: .12,
            castShadow: false,
        };

        if (width > 2.2) {
            const windowWidth = Math.max(1.1, width * .54);
            [-1, 1].forEach((side) => {
                const window = this.makeBox(windowWidth, windowHeight, .09, glassColor, room.x, windowY, -room.y + side * (depth / 2 + .05), windowOptions);
                targetGroup.add(window);
            });
        }
        if (depth > 2.2) {
            const windowDepth = Math.max(1.1, depth * .54);
            [-1, 1].forEach((side) => {
                const window = this.makeBox(.09, windowHeight, windowDepth, glassColor, room.x + side * (width / 2 + .05), windowY, -room.y, windowOptions);
                targetGroup.add(window);
            });
        }
    }

    buildUpperFloorDecks(floors) {
        floors.filter((floor) => floor.level > 0).forEach((floor) => {
            const group = this.floorGroups.get(floor.level);
            if (!group) return;
            const materialColor = floor.level === 1 ? 0x6e8790 : 0x81786f;
            const ringParts = [
                this.makeBox(84, .36, 12, materialColor, 0, floor.elevation, 30, { transparent: true, opacity: .24, castShadow: false }),
                this.makeBox(84, .36, 12, materialColor, 0, floor.elevation, -30, { transparent: true, opacity: .24, castShadow: false }),
                this.makeBox(13, .36, 48, materialColor, -34, floor.elevation, 0, { transparent: true, opacity: .24, castShadow: false }),
                this.makeBox(13, .36, 48, materialColor, 34, floor.elevation, 0, { transparent: true, opacity: .24, castShadow: false }),
            ];
            ringParts.forEach((part) => group.add(part));
            const label = this.makeLabel(`${floor.name.toUpperCase()} · 3D MODEL`, 0xffffff, 8);
            label.position.set(0, floor.elevation + 2, 0);
            group.add(label);
            label.userData.floorLevel = floor.level;
            this.labels.push(label);
        });
    }

    buildMarkers() {
        this.currentMarker = this.makeMarker(0x31e0b7, "YOU");
        this.destinationMarker = this.makeMarker(0xff5d63, "DESTINATION");
        this.sharedMarker = this.makeMarker(0x8e75ff, "SHARED USER");
        this.destinationMarker.visible = false;
        this.sharedMarker.visible = false;
        this.scene.add(this.currentMarker, this.destinationMarker, this.sharedMarker);
    }

    makeMarker(color, labelText) {
        const group = new THREE.Group();
        const stem = new THREE.Mesh(new THREE.CylinderGeometry(.12, .12, 1.5, 12), new THREE.MeshStandardMaterial({ color }));
        stem.position.y = 1.05;
        const head = new THREE.Mesh(new THREE.SphereGeometry(.55, 18, 18), new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: .4 }));
        head.position.y = 1.95;
        const ring = new THREE.Mesh(new THREE.RingGeometry(.75, 1.05, 32), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: .42, side: THREE.DoubleSide }));
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = .34;
        ring.userData.pulseRing = true;
        const label = this.makeLabel(labelText, 0xffffff, 7);
        label.position.y = 3.3;
        group.add(stem, head, ring, label);
        group.userData.ring = ring;
        return group;
    }

    addTree(x, z, group, scale = 1) {
        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(.22 * scale, .32 * scale, 2.2 * scale, 8), new THREE.MeshStandardMaterial({ color: 0x65452f, roughness: 1 }));
        trunk.position.set(x, 1.35 * scale, z);
        trunk.castShadow = true;
        const crownColor = z % 2 ? 0x356b42 : 0x477b45;
        const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(1.45 * scale, 1), new THREE.MeshStandardMaterial({ color: crownColor, roughness: 1 }));
        crown.position.set(x, 3.1 * scale, z);
        crown.castShadow = true;
        group.add(trunk, crown);
    }

    makeLabel(text, color = 0xeaf6f2, fontSize = 9) {
        const canvas = document.createElement("canvas");
        canvas.width = 320;
        canvas.height = 72;
        const context = canvas.getContext("2d");
        context.fillStyle = "rgba(5, 26, 33, .84)";
        context.beginPath();
        if (context.roundRect) context.roundRect(2, 3, 316, 66, 15);
        else context.rect(2, 3, 316, 66);
        context.fill();
        context.fillStyle = color;
        context.font = `800 ${fontSize * 2.7}px Inter, Arial`;
        context.textAlign = "center";
        context.textBaseline = "middle";
        context.fillText(text, 160, 37, 292);
        const texture = new THREE.CanvasTexture(canvas);
        texture.encoding = THREE.sRGBEncoding;
        const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false }));
        sprite.scale.set(11.5, 2.6, 1);
        sprite.renderOrder = 4;
        return sprite;
    }

    shortLabel(name) {
        return name.replace("Laboratory", "Lab").replace("Classroom", "Class").replace(" / Enquiry", "").toUpperCase();
    }

    pickRoom(event) {
        const hits = this.raycast(event);
        if (hits.length && hits[0].object.userData.roomCode) this.onRoomSelect(hits[0].object.userData.roomCode);
    }

    hoverRoom(event) {
        const hits = this.raycast(event);
        this.renderer.domElement.style.cursor = hits.length ? "pointer" : "grab";
    }

    raycast(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        this.raycaster.setFromCamera(this.pointer, this.camera);
        return this.raycaster.intersectObjects(this.selectables, false);
    }

    selectRoom(code, focus = false) {
        if (this.selectedCode && this.roomMeshes.has(this.selectedCode)) {
            const previous = this.roomMeshes.get(this.selectedCode);
            previous.material.color.setHex(previous.userData.baseColor);
            previous.material.emissive.setHex(0x000000);
            previous.material.emissiveIntensity = 0;
        }
        this.selectedCode = code;
        const mesh = this.roomMeshes.get(code);
        if (!mesh) return;
        mesh.material.color.setHex(0xff6b64);
        mesh.material.emissive.setHex(0xff352f);
        mesh.material.emissiveIntensity = .22;
        if (focus) this.focusRoom(code);
    }

    focusRoom(code) {
        const mesh = this.roomMeshes.get(code);
        if (!mesh) return;
        this.controls.target.copy(mesh.position);
        this.controls.target.y = 0;
        this.camera.position.set(mesh.position.x + 27, 30, mesh.position.z + 32);
        this.controls.update();
    }

    drawRoute(points) {
        if (this.routeObject) this.scene.remove(this.routeObject);
        const positions = points.map((point) => new THREE.Vector3(point.x, point.z + 1.05, -point.y));
        const geometry = new THREE.BufferGeometry().setFromPoints(positions);
        this.routeMaterial = new THREE.LineDashedMaterial({ color: 0xff4f58, dashSize: 1.4, gapSize: .65, linewidth: 2 });
        const line = new THREE.Line(geometry, this.routeMaterial);
        line.computeLineDistances();
        const group = new THREE.Group();
        group.add(line);
        positions.forEach((position, index) => {
            if (index === 0 || index === positions.length - 1 || index % 3 !== 0) return;
            const dot = new THREE.Mesh(new THREE.SphereGeometry(.22, 10, 10), new THREE.MeshBasicMaterial({ color: 0xff7b7f }));
            dot.position.copy(position);
            group.add(dot);
        });
        this.routeObject = group;
        this.scene.add(group);
        const last = points[points.length - 1];
        this.destinationMarker.position.set(last.x, last.z, -last.y);
        this.destinationMarker.visible = true;
    }

    clearRoute() {
        if (this.routeObject) this.scene.remove(this.routeObject);
        this.routeObject = null;
        this.destinationMarker.visible = false;
    }

    setCurrentLocation(point) {
        if (!point || !this.currentMarker) return;
        this.currentMarker.position.set(point.x, point.z || 0, -point.y);
    }

    setSharedLocation(location) {
        if (!this.sharedMarker) return;
        this.sharedMarker.position.set(location.x, location.z || 0, -location.y);
        this.sharedMarker.visible = true;
    }

    hideSharedLocation() { if (this.sharedMarker) this.sharedMarker.visible = false; }

    setFloor(level) {
        const showAll = level === "all";
        this.siteGroup.visible = showAll || Number(level) === 0;
        this.floorGroups.forEach((group, floorLevel) => {
            group.visible = showAll || Number(level) === floorLevel;
        });
        const elevation = level === "all" ? 2.5 : Number(level) * 3.66;
        this.controls.target.set(0, elevation, 0);
        this.camera.position.set(72, elevation + 72, 96);
        this.controls.update();
    }

    toggleLabels(force) {
        this.labelsVisible = typeof force === "boolean" ? force : !this.labelsVisible;
        this.labels.forEach((label) => { label.visible = this.labelsVisible; });
        return this.labelsVisible;
    }

    resetCamera() {
        this.camera.position.set(82, 84, 108);
        this.controls.target.set(0, 0, 0);
        this.controls.update();
    }

    resize() {
        const width = Math.max(1, this.container.clientWidth);
        const height = Math.max(1, this.container.clientHeight);
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height, false);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        const elapsed = this.clock.getElapsedTime();
        [this.currentMarker, this.destinationMarker, this.sharedMarker].forEach((marker, index) => {
            if (!marker || !marker.visible) return;
            const ring = marker.userData.ring;
            const scale = 1 + ((Math.sin(elapsed * 2.5 + index) + 1) * .18);
            ring.scale.setScalar(scale);
            ring.material.opacity = .36 - (scale - 1) * .55;
        });
        if (this.routeMaterial) this.routeMaterial.dashOffset = -elapsed * 1.6;
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

window.GWCET3DViewer = GWCET3DViewer;
