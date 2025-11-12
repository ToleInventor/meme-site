  // Navigation buttons
  const homeBtn = document.getElementById('home-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const profileBtn = document.getElementById('profile-btn');

  const memeFeed = document.getElementById('meme-feed');
  const uploadForm = document.getElementById('upload-form');
  const profileView = document.getElementById('profile-view');

  const followBtn = document.getElementById('follow-btn');
  const profileUsername = "{{ user_profile.username }}";
  const loggedInUser = "{{ username }}";

  if(loggedInUser && profileUsername && loggedInUser !== profileUsername){
    fetch(`/is_following/${profileUsername}`).then(r => r.json()).then(data => {
      updateFollowBtn(data.is_following);
    });
  } else {
    followBtn.style.display = 'none';
  }

  function updateFollowBtn(isFollowing){
    if(isFollowing){
      followBtn.textContent = 'Unfollow';
      followBtn.onclick = unfollow;
    } else {
      followBtn.textContent = 'Follow';
      followBtn.onclick = follow;
    }
  }

  function follow(){
    fetch(`/follow/${profileUsername}`, {method:'POST'})
    .then(r=>r.json()).then(data=>{
      if(data.status==='ok') updateFollowBtn(true);
      else alert(data.message);
    });
  }

  function unfollow(){
    fetch(`/unfollow/${profileUsername}`, {method:'POST'})
    .then(r=>r.json()).then(data=>{
      if(data.status==='ok') updateFollowBtn(false);
      else alert(data.message);
    });
  }

  homeBtn.onclick = () => {setActiveBtn(homeBtn); showSection('home');};
  uploadBtn.onclick = () => {setActiveBtn(uploadBtn); showSection('upload');};
  profileBtn.onclick = () => {setActiveBtn(profileBtn); showSection('profile');};

  function setActiveBtn(button){
    [homeBtn, uploadBtn, profileBtn].forEach(b => b.classList.remove('active'));
    button.classList.add('active');
  }

  function showSection(section){
    memeFeed.style.display = section==='home' ? 'block' : 'none';
    uploadForm.style.display = section==='upload' ? 'block' : 'none';
    profileView.style.display = section==='profile' ? 'block' : 'none';
  }

  function toggleUploadForm(show){
    if(show){
      setActiveBtn(uploadBtn);
      showSection('upload');
    } else {
      setActiveBtn(homeBtn);
      showSection('home');
    }
  }

  document.getElementById('meme_type').addEventListener('change', function(){
    const val = this.value;
    document.getElementById('text-meme-field').style.display = val === 'Text' ? 'block' : 'none';
    document.getElementById('file-upload-field').style.display = ['Image','GIF','Video'].includes(val) ? 'block' : 'none';
  });
  document.getElementById('meme_type').dispatchEvent(new Event('change'));

  document.querySelectorAll('.reaction-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const menu = btn.nextElementSibling;
      menu.classList.toggle('active');
    });
  });

  document.querySelectorAll('.reaction-emoji').forEach(emoji => {
    emoji.addEventListener('click', e => {
      const reaction = e.target.textContent;
      const memeCard = e.target.closest('.meme-card');
      const memeId = memeCard.getAttribute('data-meme-id');
      fetch(`/react/${memeId}`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({reaction})
      }).then(r=>r.json()).then(data=>{
        if(data.status==='ok'){
          alert(`Reacted with ${reaction}`);
          emoji.parentElement.classList.remove('active');
        } else alert(data.message);
      });
    });
  });

  // Show/hide comments on message toggle
  document.querySelectorAll('.message-toggle-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      const memeCard = e.target.closest('.meme-card');
      const commentsSection = memeCard.querySelector('.comments-section');
      // Hide other comments
      document.querySelectorAll('.comments-section.active').forEach(section => {
        if(section !== commentsSection) section.classList.remove('active');
      });
      commentsSection.classList.toggle('active');
    });
  });

  function performSearch(){
    const query=document.getElementById('search-bar').value.toLowerCase();
    document.querySelectorAll('.meme-card').forEach(card=>{
      const title=card.querySelector('.meme-title').textContent.toLowerCase();
      const username=card.querySelector('.meme-info').textContent.toLowerCase();
      card.style.display=(title.includes(query)|| username.includes(query))?'' : 'none';
    });
  }
  
  document.getElementById('search-form').addEventListener('submit', e=>{
    e.preventDefault();
    performSearch();
  });

  function sendComment(btn, memeId){
    const input=btn.previousElementSibling;
    const comment=input.value.trim();
    if(!comment){
      alert('Please enter a comment.');
      return;
    }
    fetch(`/comments/${memeId}`, {
      method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({comment})
    }).then(r=>r.json()).then(data=>{
      if(data.status==='ok'){
        alert('Comment sent!');
        input.value='';
      }else alert(data.message);
    });
  }