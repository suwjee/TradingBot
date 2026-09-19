import test from "node:test";
import assert from "node:assert/strict";

async function loadWorkspaceModule() {
  try {
    return await import("../src/ui/workspace-state.js");
  } catch (error) {
    assert.fail(`workspace-state module must load: ${error.message}`);
  }
}

test("workspace contracts keep chart controls exclusive to chart states", async () => {
  const { workspaceContract } = await loadWorkspaceModule();

  assert.deepEqual(workspaceContract("chart").headerGroups, [
    "chart-left",
    "drawing",
    "chart-actions",
  ]);
  assert.deepEqual(workspaceContract("fullscreen-chart").headerGroups, []);
  assert.deepEqual(workspaceContract("algorithm").headerGroups, ["workspace"]);
  assert.deepEqual(workspaceContract("faraz").headerGroups, ["workspace"]);
  assert.deepEqual(workspaceContract("algorithm").footerGroups, ["runtime", "clock"]);
});

test("unknown workspace names are rejected instead of leaking chart controls", async () => {
  const { workspaceContract } = await loadWorkspaceModule();
  assert.throws(() => workspaceContract("review"), /Unknown workspace/);
});

test("applyWorkspaceState updates visibility and accessibility from one contract", async () => {
  const { applyWorkspaceState } = await loadWorkspaceModule();
  const groups = ["chart-left", "drawing", "chart-actions", "workspace", "runtime", "market", "clock"];
  const nodes = groups.map((group) => ({
    dataset: { workspaceGroup: group },
    hidden: false,
    inert: false,
    attributes: new Map(),
    setAttribute(name, value) { this.attributes.set(name, value); },
  }));
  const root = {
    dataset: {},
    querySelectorAll() { return nodes; },
  };

  applyWorkspaceState(root, "algorithm");

  assert.equal(root.dataset.workspace, "algorithm");
  const visible = nodes.filter((node) => !node.hidden).map((node) => node.dataset.workspaceGroup);
  assert.deepEqual(visible, ["workspace", "runtime", "clock"]);
  assert.equal(nodes.find((node) => node.dataset.workspaceGroup === "drawing").attributes.get("aria-hidden"), "true");
  assert.equal(nodes.find((node) => node.dataset.workspaceGroup === "workspace").inert, false);
});

test("workspace headers move into the shared Header slot and return to their feature home", async () => {
  const { mountWorkspaceHeader, restoreWorkspaceHeader } = await loadWorkspaceModule();
  const header = { id: "algorithm-header", parentNode: null };
  const home = {
    children: [header, { id: "content" }],
    prepend(node) {
      if (node.parentNode?.children) node.parentNode.children = node.parentNode.children.filter((child) => child !== node);
      this.children = this.children.filter((child) => child !== node);
      this.children.unshift(node);
      node.parentNode = this;
    },
  };
  const slot = {
    children: [],
    hidden: true,
    replaceChildren(...nodes) {
      for (const node of nodes) {
        if (node.parentNode?.children) node.parentNode.children = node.parentNode.children.filter((child) => child !== node);
        node.parentNode = this;
      }
      this.children = nodes;
    },
  };
  header.parentNode = home;

  mountWorkspaceHeader(slot, header);
  assert.deepEqual(slot.children, [header]);
  assert.equal(slot.hidden, false);
  assert.deepEqual(home.children.map((node) => node.id), ["content"]);

  restoreWorkspaceHeader(home, header);
  assert.deepEqual(home.children.map((node) => node.id), ["algorithm-header", "content"]);
  assert.deepEqual(slot.children, []);
});
