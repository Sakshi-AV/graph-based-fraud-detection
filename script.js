function checkFraud() {

    let sender = document.getElementById("sender").value;
    let receiver = document.getElementById("receiver").value;
    let amount = document.getElementById("amount").value;
    let resultBox = document.getElementById("result");

    if (sender === "" || receiver === "" || amount === "") {
        resultBox.innerHTML = "Please fill all fields";
        resultBox.style.background = "orange";
        return;
    }

    // Dummy logic (replace with ML later)
    let probability = Math.random();

    if (probability > 0.7) {
        resultBox.innerHTML = "Fraud Detected<br>Probability: " + probability.toFixed(2);
        resultBox.style.background = "red";
    } else {
        resultBox.innerHTML = "Safe Transaction<br>Probability: " + probability.toFixed(2);
        resultBox.style.background = "green";
    }
}
