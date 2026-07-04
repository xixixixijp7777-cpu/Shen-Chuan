// Reveal page sections as they enter the viewport.
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

// Control the birthday wish modal and keyboard focus.
const modal = document.querySelector("#wishModal");
const wishButton = document.querySelector("#wishButton");
const closeButton = modal.querySelector(".modal-close");

function openModal() {
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
  closeButton.focus();
  launchFireworks();
}

function closeModal() {
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
  wishButton.focus();
}

wishButton.addEventListener("click", openModal);
modal.querySelectorAll("[data-close-modal]").forEach((item) => item.addEventListener("click", closeModal));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && modal.classList.contains("open")) closeModal();
});

// Play music only after the visitor chooses to start it.
const music = document.querySelector("#bgMusic");
const musicButton = document.querySelector("#musicButton");
const musicText = musicButton.querySelector(".music-text");
const toast = document.querySelector("#toast");
let toastTimer;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}

musicButton.addEventListener("click", async () => {
  if (!music.paused) {
    music.pause();
    musicButton.classList.remove("playing");
    musicText.textContent = "播放音乐";
    musicButton.setAttribute("aria-label", "播放背景音乐");
    return;
  }
  try {
    await music.play();
    musicButton.classList.add("playing");
    musicText.textContent = "暂停音乐";
    musicButton.setAttribute("aria-label", "暂停背景音乐");
  } catch (error) {
    showToast("请先将音乐文件放到 assets/music.mp3");
  }
});

// Draw lightweight heart trails and a small firework celebration.
const canvas = document.querySelector("#effectsCanvas");
const context = canvas.getContext("2d");
const particles = [];
let width = 0;
let height = 0;
let lastHeartTime = 0;

function resizeCanvas() {
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function addHeart(x, y) {
  particles.push({ type: "heart", x, y, vx: (Math.random() - .5) * .5, vy: -0.7 - Math.random(), life: 1, size: 7 + Math.random() * 6, color: Math.random() > .5 ? "#637fd2" : "#8b7bd8" });
}

function launchFireworks() {
  const colors = ["#6687d8", "#8b7cdb", "#62a8d5", "#e8bd70"];
  [0.3, 0.5, 0.7].forEach((position, burstIndex) => {
    setTimeout(() => {
      const centerX = width * position;
      const centerY = height * (0.25 + Math.random() * .22);
      for (let i = 0; i < 28; i += 1) {
        const angle = (Math.PI * 2 * i) / 28;
        const speed = 1.4 + Math.random() * 2.2;
        particles.push({ type: "spark", x: centerX, y: centerY, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed, life: 1, size: 2 + Math.random() * 2, color: colors[burstIndex % colors.length] });
      }
    }, burstIndex * 180);
  });
}

function animateParticles() {
  context.clearRect(0, 0, width, height);
  for (let i = particles.length - 1; i >= 0; i -= 1) {
    const particle = particles[i];
    particle.x += particle.vx;
    particle.y += particle.vy;
    if (particle.type === "spark") particle.vy += .018;
    particle.life -= particle.type === "heart" ? .018 : .012;
    context.save();
    context.globalAlpha = Math.max(particle.life, 0);
    context.fillStyle = particle.color;
    if (particle.type === "heart") {
      context.font = `${particle.size}px Arial`;
      context.fillText("♥", particle.x, particle.y);
    } else {
      context.beginPath();
      context.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      context.fill();
    }
    context.restore();
    if (particle.life <= 0) particles.splice(i, 1);
  }
  requestAnimationFrame(animateParticles);
}

window.addEventListener("resize", resizeCanvas);
document.addEventListener("pointermove", (event) => {
  if (event.pointerType !== "mouse") return;
  const now = performance.now();
  if (now - lastHeartTime > 90) {
    addHeart(event.clientX + 5, event.clientY - 5);
    lastHeartTime = now;
  }
});
document.addEventListener("pointerdown", (event) => {
  for (let i = 0; i < 5; i += 1) addHeart(event.clientX + (Math.random() - .5) * 24, event.clientY + (Math.random() - .5) * 18);
});

resizeCanvas();
animateParticles();
