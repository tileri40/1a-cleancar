(() => {
  const video = document.getElementById('work-video');
  if (!video) return;
  const start = document.getElementById('work-video-start');
  const sound = document.getElementById('work-video-sound');
  const status = document.getElementById('work-video-status');
  let inside = false;
  let attempted = false;
  const update = () => {
    sound.textContent = video.muted ? 'Ton einschalten' : 'Ton ausschalten';
    sound.setAttribute('aria-pressed', String(video.muted));
  };
  const play = async () => {
    try {
      await video.play();
      start.hidden = true;
      status.textContent = '';
    } catch {
      start.hidden = false;
      status.textContent = 'Tippen Sie auf „Video mit Ton starten“, um die Wiedergabe zu starten.';
    }
  };
  start.addEventListener('click', () => {
    video.muted = false;
    update();
    play();
  });
  sound.addEventListener('click', () => {
    video.muted = !video.muted;
    update();
    if (video.paused && inside) play();
  });
  video.addEventListener('volumechange', update);
  video.addEventListener('play', () => { start.hidden = true; status.textContent = ''; });
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inside = entries[0].isIntersecting;
      if (inside && !attempted && !reduced) {
        attempted = true;
        play();
      } else if (!inside) video.pause();
    }, {threshold: 0.35}).observe(video);
  } else { start.hidden = false; }
  if (reduced) start.hidden = false;
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) video.pause();
  });
  update();
})();
