$(document).ready(function () {
    $.get("/repos.json?2", function (repos) {
        const numR = repos.filter(r => r.language === "r").length;
        const numPy = repos.filter(r => r.language === "python").length;
        const numJs = repos.filter(r => r.language === "js" || r.language === "typescript").length;
        const numTot = repos.length;

        const langs = [...new Set(repos.map(r => r.language))];
        const numLangs = langs.map(l => ({l: l, n: repos.filter(r => r.language === l).length}))
            .sort((x, y) => y.n - x.n);

        console.log(langs)
        console.log(numLangs)
        const pieData = {
            labels: [
                'R',
                'Python',
                "Javascript",
                'Other'
            ],
            datasets: [{
                label: 'Language',
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgb(100, 100, 100, 0.8)'
                ],
                hoverOffset: 4,
                data: [numR,
                    numPy,
                    numJs,
                    numTot - numPy - numR - numJs]
            }]
        };

        new Chart(
            document.getElementById('pieChart'),
            {
                type: 'pie',
                data: pieData,
            }
        );

        const mostUsed = repos.filter(r => r.used_by.length > 0)
            .sort((a, b) => b.used_by.length - a.used_by.length)
            .slice(0, 6);

        const barData = {
            labels: mostUsed.map(r => r.name),
            datasets: [{
                label: 'Most depended on',
                hoverOffset: 4,
                data: mostUsed.map(r => r.used_by.length),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(201, 203, 207, 0.8)'
                ],
            }]
        };

        new Chart(
            document.getElementById('barChart'),
            {
                type: 'bar',
                data: barData,
            }
        );
    })
});
