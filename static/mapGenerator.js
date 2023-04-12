var clickCount = 0
var firstClick = [];
var secondClick = [];

document.getElementById("generate-btn").addEventListener("click", function() {
    fetch("/generate-map")
      .then(response => {
        return response.text();
      })
      .then(data => {
        const timestamp = new Date().getTime();
        const imageUrl = data + '?_=' + timestamp;
        document.getElementById("map-container").innerHTML = "<img src='" + imageUrl + "'>";
        document.getElementById("map-container").addEventListener("click", handleImageClick)
      });
  });

function handleImageClick(event) {
    clickCount++;
    if (clickCount > 0) {
        var x = event.offsetX;
        var y = event.offsetY;
        if (clickCount%2 == 1) {
            firstClick[0] = x;
            firstClick[1] = y;
        } else {
            secondClick[0] = x;
            secondClick[1] = y;
            document.getElementById("loading-text").style.display = "block";
            var formData = new FormData();
            formData.append('x1', firstClick[0]);
            formData.append('y1', firstClick[1]);
            formData.append('x2', secondClick[0]);
            formData.append('y2', secondClick[1]);
            fetch("/generate-route", {
                method: "POST",
                body: formData
            })
            .then(response => {
                return response.text();
            })
            .then(data => {
                const timestamp = new Date().getTime();
                const imageUrl = data + '?_=' + timestamp;
                document.getElementById("map-container").innerHTML = "<img src='" + imageUrl + "'>";
                document.getElementById("loading-text").style.display = "none";
            });
        }
    }
}

