/**
 * CineMitra - Movies. Magic. Memories.
 * Comprehensive Client-Side Application Script
 */

// Global State Helpers
const CineMitra = {
  // Get currently selected city
  getCity() {
    return localStorage.getItem('cinemitra_city') || 'Pune';
  },
  setCity(city) {
    localStorage.setItem('cinemitra_city', city);
    this.updateNavCity();
  },

  // User auth state
  getUser() {
    const raw = localStorage.getItem('cinemitra_user');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },
  setUser(userData) {
    localStorage.setItem('cinemitra_user', JSON.stringify(userData));
    this.updateNavUser();
  },
  logout() {
    localStorage.removeItem('cinemitra_user');
    this.updateNavUser();
    CineMitra.toast("Signed out successfully");
    setTimeout(() => {
      window.location.href = "signin.html";
    }, 800);
  },

  // Selected Booking Details
  getTheater() {
    const raw = localStorage.getItem('cinemitra_theater');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },
  setTheater(theater) {
    localStorage.setItem('cinemitra_theater', JSON.stringify(theater));
  },

  getMovie() {
    const raw = localStorage.getItem('cinemitra_movie');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },
  setMovie(movie) {
    localStorage.setItem('cinemitra_movie', JSON.stringify(movie));
  },

  getShow() {
    const raw = localStorage.getItem('cinemitra_show');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  },
  setShow(showData) {
    localStorage.setItem('cinemitra_show', JSON.stringify(showData));
  },

  // Toast Notification
  toast(message, duration = 3000) {
    let container = document.getElementById('cinemitra-toast');
    if (!container) {
      container = document.createElement('div');
      container.id = 'cinemitra-toast';
      container.className = 'toast';
      document.body.appendChild(container);
    }
    container.textContent = message;
    container.classList.add('show');
    setTimeout(() => {
      container.classList.remove('show');
    }, duration);
  },

  // Update navigation items
  updateNavCity() {
    const cityEl = document.getElementById('nav-current-city');
    if (cityEl) {
      cityEl.textContent = this.getCity();
    }
  },
  updateNavUser() {
    const user = this.getUser();
    const userBtn = document.getElementById('nav-user-btn');
    if (userBtn) {
      if (user && user.isLoggedIn) {
        userBtn.innerHTML = `<span>👤</span> ${user.name || user.email.split('@')[0]} <span style="font-size:0.75rem; opacity:0.7; margin-left:4px;">(Logout)</span>`;
        userBtn.href = "#";
        userBtn.onclick = (e) => {
          e.preventDefault();
          CineMitra.logout();
        };
      } else {
        userBtn.innerHTML = `<span>Sign In</span>`;
        userBtn.href = "signin.html";
        userBtn.onclick = null;
      }
    }
  },

  // Generate safe movie card HTML with guaranteed poster fallback
  createMovieCard(movie, actionBtnText = "Book Tickets", customReason = null) {
    const movieJson = encodeURIComponent(JSON.stringify(movie));
    const safeTitle = (movie['Movie Name'] || 'Unknown Movie').replace(/"/g, '&quot;');
    const year = movie['Year'] || '2024';
    const lang = movie['Language'] || 'Hindi';
    const rating = movie['Rating(10)'] ? parseFloat(movie['Rating(10)']).toFixed(1) : '7.5';
    const genre = movie['Genre'] || 'Drama';
    const posterUrl = movie['Poster'] || '';

    return `
      <div class="movie-card" id="movie-card-${movie.ID}">
        <div class="poster-wrapper">
          <img 
            class="poster-img" 
            src="${posterUrl}" 
            alt="${safeTitle} Poster" 
            loading="lazy"
            onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
          />
          <div class="poster-fallback" style="display: ${posterUrl ? 'none' : 'flex'};">
            <div class="poster-fallback-top">
              <span class="badge-overlay-lang" style="position:static;">${lang}</span>
              <span class="poster-fallback-reel">🎬</span>
            </div>
            <div>
              <div class="poster-fallback-title">${safeTitle}</div>
              <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">${year} • ${genre}</div>
            </div>
          </div>
          <span class="badge-overlay-lang">${lang}</span>
          <span class="badge-overlay-rating">⭐ ${rating}</span>
        </div>
        <div class="movie-card-body">
          <div class="movie-title" title="${safeTitle}">${safeTitle}</div>
          <div class="movie-meta-line">
            <span>📅 ${year}</span>
            <span>⏱️ ${movie['Timing(min)'] || 140} min</span>
          </div>
          <div class="movie-genre" title="${genre}">${genre}</div>
          ${customReason ? `<div class="recommendation-reason-badge">💡 ${customReason}</div>` : ''}
          <div class="movie-card-footer">
            <button class="btn-book-card" onclick="CineMitra.selectMovieAndProceed('${movieJson}')">
              ${actionBtnText}
            </button>
          </div>
        </div>
      </div>
    `;
  },

  selectMovieAndProceed(encodedMovieJson) {
    try {
      const movie = JSON.parse(decodeURIComponent(encodedMovieJson));
      this.setMovie(movie);
      // If user hasn't selected city or theater yet, ensure city is set
      if (!this.getTheater()) {
        const city = this.getCity();
        this.setTheater({
          id: `${city.toLowerCase()}-1`,
          name: `PVR Cinemas, ${city}`,
          city: city,
          area: "City Center"
        });
      }
      window.location.href = "shows.html";
    } catch (e) {
      console.error("Error selecting movie:", e);
      window.location.href = "movies.html";
    }
  }
};

// Initialize global nav listeners on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  CineMitra.updateNavCity();
  CineMitra.updateNavUser();

  // Search input in header
  const headerSearchInput = document.getElementById('nav-search-input');
  if (headerSearchInput) {
    headerSearchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = encodeURIComponent(headerSearchInput.value.trim());
        window.location.href = `movies.html?search=${query}`;
      }
    });
  }
});
