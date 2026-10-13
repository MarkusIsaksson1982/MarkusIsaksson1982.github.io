/** Build a canonical person node id from an email address. */
export function personId(email) {
    return 'person:' + email.trim().toLowerCase();
}
/** In-memory person/company/stage graph with attached inbox events. */
export class MemoryGraph {
    nodeMap = new Map();
    edgeMap = new Map();
    events = [];
    /** Insert a node uniquely by id, with placeholder-label upgrade. */
    addNode(node) {
        const existing = this.nodeMap.get(node.id);
        if (existing === undefined) {
            this.nodeMap.set(node.id, { ...node });
            return;
        }
        if (existing.label === existing.id && node.label !== existing.id) {
            existing.label = node.label;
        }
    }
    /** Insert an edge uniquely by from+to+rel, keeping the latest `at`. */
    addEdge(edge) {
        const key = `${edge.from}\0${edge.to}\0${edge.rel}`;
        const existing = this.edgeMap.get(key);
        if (existing === undefined) {
            this.edgeMap.set(key, { ...edge });
            return;
        }
        if (edge.at > existing.at) {
            this.edgeMap.set(key, { ...edge });
        }
    }
    /** Store an event and project its person/company/stage nodes and edges. */
    ingest(ev) {
        this.events.push({ ...ev });
        const pid = personId(ev.person);
        this.addNode({ id: pid, type: 'person', label: ev.name ?? pid });
        if (ev.company) {
            const cid = 'company:' + ev.company.trim().toLowerCase();
            this.addNode({ id: cid, type: 'company', label: ev.company });
            this.addEdge({ from: pid, to: cid, rel: 'works_at', at: ev.at });
        }
        if (ev.kind === 'crm_stage_changed' && ev.stage && ev.company) {
            const cid = 'company:' + ev.company.trim().toLowerCase();
            const sid = 'stage:' + ev.stage.trim().toLowerCase();
            this.addNode({ id: sid, type: 'stage', label: ev.stage });
            this.addEdge({ from: cid, to: sid, rel: 'in_stage', at: ev.at });
        }
    }
    /** List nodes in insertion order. */
    nodes() {
        return [...this.nodeMap.values()].map((n) => ({ ...n }));
    }
    /** List edges in insertion order. */
    edges() {
        return [...this.edgeMap.values()].map((e) => ({ ...e }));
    }
    /** List unique connected ids in either direction, sorted. */
    neighbors(id) {
        const found = new Set();
        for (const e of this.edgeMap.values()) {
            if (e.from === id) {
                found.add(e.to);
            }
            else if (e.to === id) {
                found.add(e.from);
            }
        }
        return [...found].sort();
    }
    /** List stored events for a person id, sorted by `at` ascending. */
    history(id) {
        return this.events
            .filter((e) => personId(e.person) === id)
            .sort((a, b) => (a.at < b.at ? -1 : a.at > b.at ? 1 : 0))
            .map((e) => ({ ...e }));
    }
}
