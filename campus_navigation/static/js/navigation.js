// navigation.js - A* Pathfinding Logic

class PriorityQueue {
    constructor() { this.elements = []; }
    enqueue(item, priority) {
        this.elements.push({item, priority});
        this.elements.sort((a, b) => a.priority - b.priority);
    }
    dequeue() { return this.elements.shift().item; }
    isEmpty() { return this.elements.length === 0; }
}

class Navigator {
    constructor(dataUrl) {
        this.nodes = {};
        this.edges = {};
        // Consumers can await this before using either the graph or a scene
        // derived from it. Keep the rejection intact so the UI can report it.
        this.ready = this.loadData(dataUrl);
    }

    async loadData(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Ground-floor map request failed (${response.status}).`);
        }

        let data;
        try {
            data = await response.json();
        } catch (error) {
            throw new Error("Ground-floor map data is not valid JSON.");
        }

        if (!data?.nodes || typeof data.nodes !== "object" || !Array.isArray(data.edges)) {
            throw new Error("Ground-floor map data is missing nodes or edges.");
        }

        const edges = {};
        for (const key in data.nodes) {
            edges[key] = [];
        }

        data.edges.forEach((edge) => {
            const [n1, n2] = edge;
            if (data.nodes[n1] && data.nodes[n2]) {
                edges[n1].push(n2);
                edges[n2].push(n1);
            }
        });

        this.nodes = data.nodes;
        this.edges = edges;
        return data;
    }

    heuristic(nodeA, nodeB) {
        const a = this.nodes[nodeA];
        const b = this.nodes[nodeB];
        // Manhattan distance approximation (since mostly 2D layout)
        return Math.abs(a.x - b.x) + Math.abs(a.z - b.z);
    }

    findPath(start, goal) {
        if (!this.nodes[start] || !this.nodes[goal]) return null;

        const frontier = new PriorityQueue();
        frontier.enqueue(start, 0);
        
        const cameFrom = {};
        const costSoFar = {};
        
        cameFrom[start] = null;
        costSoFar[start] = 0;

        while (!frontier.isEmpty()) {
            const current = frontier.dequeue();

            if (current === goal) break;

            this.edges[current].forEach(next => {
                const newCost = costSoFar[current] + this.heuristic(current, next); // Assume edge cost ~ heuristic
                if (!(next in costSoFar) || newCost < costSoFar[next]) {
                    costSoFar[next] = newCost;
                    const priority = newCost + this.heuristic(next, goal);
                    frontier.enqueue(next, priority);
                    cameFrom[next] = current;
                }
            });
        }

        // Reconstruct path
        let current = goal;
        const path = [];
        if (!(current in cameFrom)) return null; // Path not found

        while (current !== start) {
            path.push(current);
            current = cameFrom[current];
        }
        path.push(start);
        path.reverse();
        return path;
    }
}

// Instantiate Navigator globally
window.campusNavigator = new Navigator('/static/data/ground_floor.json');
