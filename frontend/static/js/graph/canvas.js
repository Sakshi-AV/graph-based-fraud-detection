import { shortId } from "../utils.js";
import { buildGraph } from "./model.js";

export function drawNetwork(transactions) {
  const canvas = document.getElementById("networkCanvas");
  if (!canvas) {
    return;
  }

  const ctx = canvas.getContext("2d");
  const graph = buildGraph(transactions);
  const nodes = [...graph.nodes.keys()];
  const width = canvas.width;
  const height = canvas.height;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#0e141a";
  ctx.fillRect(0, 0, width, height);

  const positions = new Map();
  nodes.forEach((id, index) => {
    const angle = (Math.PI * 2 * index) / nodes.length - Math.PI / 2;
    positions.set(id, {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius
    });
  });

  graph.edges.slice(-24).forEach((edge) => {
    const source = positions.get(edge.source);
    const target = positions.get(edge.target);
    if (!source || !target) {
      return;
    }

    ctx.strokeStyle = edge.risk >= 70 ? "rgba(255,107,107,0.82)" : "rgba(94,177,255,0.38)";
    ctx.lineWidth = Math.max(1, Math.min(5, Math.log10(edge.amount + 1)));
    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    ctx.lineTo(target.x, target.y);
    ctx.stroke();
  });

  nodes.forEach((id) => {
    const node = graph.nodes.get(id);
    const position = positions.get(id);
    const nodeRadius = 7 + Math.min(10, node.degree * 1.4);

    ctx.beginPath();
    ctx.fillStyle = node.pageRank > 0.16 ? "#f5c451" : "#44d19d";
    ctx.arc(position.x, position.y, nodeRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#dbe5ed";
    ctx.font = "12px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(shortId(id), position.x, position.y + nodeRadius + 16);
  });
}

