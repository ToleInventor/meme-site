// Toggle floating navigation visibility
const navToggleBtn = document.getElementById('nav-toggle-btn');
const floatingNav = document.getElementById('floating-nav');
navToggleBtn.addEventListener('click', () => {
  floatingNav.style.display = (floatingNav.style.display === 'flex') ? 'none' : 'flex';
});

// Navigation buttons switch sections
const btnHome = document.getElementById('btn-home');
const btnUpload = document.getElementById('btn-upload');
const btnProfile = document.getElementById('btn-profile');
const btnDiscover = document.getElementById('btn-discover');
const sections = {
  home: document.getElementById('home'),
  upload: document.getElementById('upload'),
  profile: document.getElementById('profile'),
  discover: document.getElementById('discover'),
};
function setActiveNav(activeButton, activeSection) {
  [btnHome, btnUpload, btnProfile, btnDiscover].forEach(btn => btn.classList.remove('active'));
  activeButton.classList.add('active');
  Object.values(sections).forEach(section => section.style.display = 'none');
  activeSection.style.display = 'block';
}
btnHome.onclick = () => setActiveNav(btnHome, sections.home);
btnUpload.onclick = () => setActiveNav(btnUpload, sections.upload);
btnProfile.onclick = () => setActiveNav(btnProfile, sections.profile);
btnDiscover.onclick = () => setActiveNav(btnDiscover, sections.discover);

// Meme search prefix match on submit
document.getElementById('search-form').addEventListener('submit', event => {
  event.preventDefault();
  const query = document.getElementById('search-bar').value.trim().toLowerCase();

  if (!query) {
    document.querySelectorAll('.meme-card').forEach(card => card.style.display = '');
    return;
  }

  const queryWords = query.split(/\s+/);

  document.querySelectorAll('.meme-card').forEach(card => {
    const title = card.querySelector('.meme-title')?.textContent.toLowerCase() || '';
    const username = card.querySelector('.meme-info')?.textContent.toLowerCase() || '';
    const matches = queryWords.some(word => title.startsWith(word) || username.startsWith(word));
    card.style.display = matches ? '' : 'none';
  });
});

// Reaction toggle menu
document.querySelectorAll('.reaction-toggle-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.nextElementSibling.classList.toggle('active');
  });
});

// Reaction emoji submit (Ajax simulation)
document.querySelectorAll('.reaction-emoji').forEach(emoji => {
  emoji.addEventListener('click', e => {
    const reaction = e.target.textContent;
    // Simulate backend posting reaction here
    alert(`Reacted with ${reaction}`);
    e.target.parentElement.classList.remove('active');
  });
});

// Comments toggle
document.querySelectorAll('.message-toggle-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    const memeCard = e.target.closest('.meme-card');
    const commentsSection = memeCard.querySelector('.comments-section');
    document.querySelectorAll('.comments-section.active').forEach(sec => {
      if (sec !== commentsSection) sec.classList.remove('active');
    });
    commentsSection.classList.toggle('active');
  });
});

// Send comment simulation
function sendComment(button, memeId) {
  const input = button.previousElementSibling;
  if (!input.value.trim()) {
    alert('Please enter a comment.');
    return;
  }
  alert(`Comment sent: "${input.value.trim()}" on meme ${memeId}`);
  input.value = '';
}

// Discover user search debounce + Ajax simulation
const discoverInput = document.getElementById('discover-search');
const discoverResults = document.getElementById('discover-results');
const userMemesContainer = document.getElementById('user-memes');
let debounceTimer = null;
discoverInput.addEventListener('input', () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    const query = discoverInput.value.trim();
    if (!query) {
      discoverResults.innerHTML = '';
      userMemesContainer.innerHTML = '';
      return;
    }
    // Simulate ajax search users
    discoverResults.innerHTML = `<p>Searching users for '${query}'...</p>`;
    setTimeout(() => {
      // Simulated search results (replace with real ajax call)
      discoverResults.innerHTML = `
        <div class="user-result">
          <div class="user-info">
            <img src="/static/default-profile.png" alt="user1"/>
            <span class="user-name">user1</span>
          </div>
          <button class="follow-btn">Follow</button>
        </div>
      `;
      userMemesContainer.innerHTML = '';
    }, 500);
  }, 300);
});
