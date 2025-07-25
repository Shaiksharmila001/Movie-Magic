const searchInput = document.getElementById("searchInput");
const movieCards = document.querySelectorAll(".movie-card");

searchInput.addEventListener("input", function () {
  const query = searchInput.value.toLowerCase();

  movieCards.forEach(function (card) {
    const movieName = card.querySelector(".movie-name").textContent.toLowerCase();
    if (movieName.includes(query)) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
});

function goBack() {
  window.history.back();
}
function goBack() {
  window.history.back();
}