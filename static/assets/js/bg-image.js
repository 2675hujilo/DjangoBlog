function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
}

var randomIndex = getRandomInt(1, 9);
var heroSection = document.getElementById("back-image-all");
heroSection.style.backgroundImage = "url('/static/images/pic/pic_0" + randomIndex + ".png')";
var randomIndex1 = getRandomInt(1, 9);
var heroSection1 = document.getElementById("hero-section");
heroSection1.style.backgroundImage = "url('/static/images/pic/pic_0" + randomIndex1 + ".png')";

