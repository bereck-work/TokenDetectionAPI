let boxList ;
let targetNumber ;
let startTime ;
let gameClock ;

window.addEventListener("load",initGame);

function initGame(){
// Initializes the game.
    targetNumber = 1 ;
    startTime = NaN ;
    boxList = [...document.querySelectorAll(".box")] ;
    boxList.forEach((inputField,i) => {
        inputField.addEventListener("click",() => markCell(`${i}`)) ;
    });
};

function fillRandom(){
    let numbers = [] ;
    for(i = 1;i<26;i++) numbers.push(i) ;
    for(i = 0;i<boxList.length;i++) {
        let number = numbers[Math.floor(Math.random() * numbers.length)] ;
        boxList[i].innerHTML = `<div class="num">${number}</div>` ;
        boxList[i].value = number ;
        numbers = numbers.filter(n => n != boxList[i].innerText) ;
    }
}

function statGame(event){
    targetNumber = 1 ;
    startTime = performance.now();

    // hide the page
    event.target.parentNode.setAttribute("data-state","hidden");

    // generate random numbers
    fillRandom();

    // clear Marked States
    boxList.forEach((inputField,i) => {
        inputField.setAttribute("data-marked","false") ;
    });

    // start clock
    timer.innerText = `0s` ;
    scorePageTime.innerHTML = `0s` ;
    gameClock = setInterval(clockTick,1000) ;
}

function check(clickedNumber){
    if(clickedNumber == targetNumber) {
        targetNumber++ ;
    } else {
        gameOver();
    }
    if(targetNumber >= 26) {
        showScore();
    }
}

function clockTick(){
    let seconds = Math.floor((performance.now() - startTime)/1000) ;
    let minutes = Math.floor(seconds / 60) ;
    if(minutes > 0) {
        timer.innerText = `${minutes}m ${seconds%60}s` ;
        scorePageTime.innerHTML = `${minutes}m ${seconds%60}s` ;
    } else {
        timer.innerText = `${seconds%60}s` ;
        scorePageTime.innerText = `${seconds%60}s` ;
    }
}

function markCell(index){
    boxList[index].setAttribute("data-marked","true") ;
    check(boxList[index].querySelector(".num").innerText);
}

function showScore(){
    scoreScreen.setAttribute("data-state","visible") ;
    clearInterval(gameClock);
}

function gameOver(){
    clearInterval(gameClock);
    gameOverScreen.setAttribute("data-state","visible") ;
}