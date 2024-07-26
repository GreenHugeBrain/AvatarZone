let aboutUs = document.querySelector('.aboutus');
let aboutProject = document.querySelector('.aboutproject');
let ourProject = document.querySelector('.ourproduct');
let thingsDiv = document.querySelector('.things-div');
let thingsdivtitle = document.querySelector('.things-div-title');

function showThingsDiv(title, height) {
    thingsDiv.style.height = height + 'px';
    thingsDiv.style.opacity = '1';
    thingsdivtitle.textContent = title;

    thingsDiv.innerHTML = '';

    if (title === 'ჩვენი პროდუქტი') {
        thingsDiv.innerHTML = `
            <section class="finder">
                <h3>STEAM FINDER</h3>
                <p>სანამ წვდომას მიიღებდეთ ჩვენს Steam Finder - ზე მანამდე გადაიხადეთ!</p>
                <div class="servicefutures">
                    <ul>
                        <h3>ფასები</h3>
                        <hr>
                        <p>SteamFinder - ფასი - 5 დღით: 16.99₾</p>
                        <p>მინუსები: 3 საათი ჰოლდი</p>
                        <hr>
                        <p>SteamFinder - ფასი - 2 კვირით: 45.99₾</p>
                        <p>მინუსები: 8 საათი ჰოლდი</p>
                        <p>ბენეფიტები: მეტი რექუესტი</p>
                        <hr>
                        <p>SteamFinder - ფასი - 1 თვით: 399.99₾</p>
                        <p>ბენეფიტები: მეტი რექუესტი, სრული პროდუქტი</p>
                        <hr>
                        <a href="/pay"><button class="pay">რეგისტრაცია</button></a>
                    </ul>
                </div>
            </section>
        `;
    }
}

aboutUs.addEventListener('click', function() {
    showThingsDiv('ჩვენს შესახებ', 800);
});

aboutProject.addEventListener('click', function() {
    showThingsDiv('პროექტის შესახებ', 800);
});

ourProject.addEventListener('click', function() {
    showThingsDiv('ჩვენი პროდუქტი', 1000);
});
