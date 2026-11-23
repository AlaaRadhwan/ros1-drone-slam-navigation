var freeButtonActive = true;
var squareButtonActive = false;

function selectNavOption(optionId) {
    var freeButton = document.getElementById('freeButton');
    var squareButton = document.getElementById('squareButton');

    if (optionId === 'free') {
        console.log('free button was clicked');
        freeButton.classList.add('active');
        squareButton.classList.remove('active');
        localStorage.setItem('navChoice', 'free');

        freeButtonActive = true;
        squareButtonActive = false;

    } else if (optionId === 'square'){
        console.log('square button was clicked');
        freeButton.classList.remove('active');
        squareButton.classList.add('active');
        localStorage.setItem('navChoice', 'square');

        freeButtonActive = false;
        squareButtonActive = true;
    }


    console.log("free button active: ", freeButtonActive);
    console.log("square button: ", squareButtonActive);
}


