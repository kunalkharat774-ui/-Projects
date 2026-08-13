from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MathMaster Pro - 1000 Quiz Challenge</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cinzel:wght@700&display=swap" rel="stylesheet">
    <style>
        .certificate-font { font-family: 'Cinzel', serif; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
        
        /* Custom Blue & Golden Glow Effects */
        .gold-gradient-text {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .blue-gold-glow {
            box-shadow: 0 0 25px rgba(245, 158, 11, 0.15), inset 0 0 15px rgba(30, 58, 138, 0.3);
        }
    </style>
</head>
<body class="bg-[#070b19] text-blue-50 font-['Inter'] min-h-screen flex flex-col justify-between selection:bg-amber-500 selection:text-slate-950">

    <!-- Header -->
    <header class="border-b border-blue-900/40 bg-[#0b132b]/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-br from-amber-400 to-amber-600 p-2.5 rounded-xl shadow-lg shadow-amber-500/20 text-slate-950">
                    <i class="fa-solid fa-square-root-variable text-xl font-black"></i>
                </div>
                <span class="font-bold text-xl tracking-tight gold-gradient-text">MathMaster Pro</span>
            </div>
            <div id="user-stats" class="hidden flex items-center space-x-6 text-sm">
                <div class="bg-blue-950/60 border border-blue-800/50 px-3 py-1 rounded-full"><i class="fa-solid fa-fire text-amber-400 mr-2"></i>Day <span id="current-day-badge" class="font-semibold text-white">1</span> / 10</div>
                <div class="bg-blue-950/60 border border-blue-800/50 px-3 py-1 rounded-full"><i class="fa-solid fa-trophy text-amber-400 mr-2"></i>Score: <span id="total-score" class="font-semibold text-white">0</span>/1000</div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-4xl mx-auto px-6 py-12 flex-grow w-full">
        
        <!-- View 1: Dashboard / Day Selector -->
        <div id="view-dashboard" class="animate-fade-in">
            <div class="text-center max-w-2xl mx-auto mb-12">
                <h1 class="text-4xl font-extrabold tracking-tight mb-4 sm:text-5xl text-white">1,000-Problem <span class="gold-gradient-text">Mathematical Challenge</span></h1>
                <p class="text-blue-200/70 text-lg">Master advanced arithmetic, algebra, and logic. Complete 100 problems daily across 10 structured days to earn your professional certificate.</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4" id="days-grid">
                <!-- Dynamically injected days -->
            </div>
        </div>

        <!-- View 2: Quiz Interface -->
        <div id="view-quiz" class="hidden animate-fade-in">
            <div class="bg-[#0f172a] border border-blue-900/50 rounded-2xl p-8 shadow-2xl relative overflow-hidden blue-gold-glow">
                <div class="flex justify-between items-center mb-8 pb-4 border-b border-blue-900/40">
                    <div>
                        <span id="quiz-day-tag" class="text-xs uppercase tracking-wider bg-amber-500/10 text-amber-400 px-3 py-1 rounded-full font-semibold border border-amber-500/30">Day 1</span>
                        <h2 class="text-2xl font-bold mt-2 text-white" id="quiz-progress-text">Problem 1 of 100</h2>
                    </div>
                    <button onclick="returnToDashboard()" class="text-blue-300 hover:text-amber-400 transition text-sm flex items-center space-x-2 bg-blue-950/80 px-3 py-1.5 rounded-lg border border-blue-800/50">
                        <i class="fa-solid fa-arrow-left"></i><span>Dashboard</span>
                    </button>
                </div>

                <!-- Problem Card -->
                <div class="text-center py-8">
                    <div id="question-box" class="text-4xl sm:text-5xl font-extrabold tracking-wide mb-8 text-amber-300">
                        <!-- Math question goes here -->
                    </div>
                    <div class="max-w-xs mx-auto">
                        <input type="number" id="answer-input" placeholder="Enter answer" class="w-full bg-[#070b19] border border-blue-800 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 rounded-xl px-4 py-3 text-center text-2xl font-bold text-white outline-none transition">
                        <button onclick="submitAnswer()" class="w-full mt-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold py-3.5 rounded-xl shadow-lg shadow-amber-500/20 transition transform active:scale-95">
                            Submit Answer <i class="fa-solid fa-arrow-right ml-2"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- View 3: Certificate View -->
        <div id="view-certificate" class="hidden animate-fade-in">
            <div class="bg-slate-900 border-8 border-double border-amber-500 rounded-3xl p-8 sm:p-12 shadow-2xl relative text-center text-slate-900 bg-gradient-to-b from-blue-50 via-white to-blue-100" id="certificate-box">
                <div class="absolute top-6 left-6 text-amber-600 text-3xl"><i class="fa-solid fa-award"></i></div>
                <div class="absolute top-6 right-6 text-amber-600 text-3xl"><i class="fa-solid fa-certificate"></i></div>
                
                <h4 class="text-xs uppercase tracking-[0.3em] font-bold text-blue-900 mb-2">Certificate of Professional Achievement</h4>
                <h2 class="certificate-font text-3xl sm:text-4xl font-bold text-blue-950 mb-4">MathMaster Expert</h2>
                
                <p class="text-blue-900/80 text-sm mb-6">This official credential certifies that</p>
                <h3 class="text-3xl font-extrabold text-blue-900 border-b-2 border-amber-500 pb-2 inline-block px-8 mb-6" id="cert-holder-name">Dedicated Scholar</h3>
                
                <p class="text-slate-700 max-w-xl mx-auto text-sm leading-relaxed mb-8">
                    Has successfully completed the rigorous 1,000-problem quantitative curriculum spanning 10 intensive modules, demonstrating exceptional aptitude in numerical analysis, algebra, and problem solving.
                </p>

                <div class="flex justify-around items-center pt-6 border-t border-blue-200 text-xs text-blue-900">
                    <div>
                        <p class="font-bold text-blue-950" id="cert-date">Date Issued</p>
                        <p>Completion Date</p>
                    </div>
                    <div class="bg-amber-500 text-white p-3 rounded-full shadow-md">
                        <i class="fa-solid fa-check text-xl"></i>
                    </div>
                    <div>
                        <p class="font-bold text-blue-950">ID: MM-1000-VERIFIED</p>
                        <p>Verified Credential</p>
                    </div>
                </div>

                <div class="mt-8 flex justify-center space-x-4">
                    <button onclick="window.print()" class="bg-blue-950 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-blue-900 transition shadow-md">
                        <i class="fa-solid fa-print mr-2"></i> Print Certificate
                    </button>
                    <button onclick="returnToDashboard()" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-sm transition shadow-md">
                        Dashboard
                    </button>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="border-t border-blue-900/40 py-6 text-center text-xs text-blue-400/60 bg-[#050813]">
        &copy; 2026 MathMaster Pro Systems. All rights reserved. 
    </footer>

    <!-- JavaScript Game Logic -->
    <script>
        const TOTAL_DAYS = 10;
        const PROBLEMS_PER_DAY = 100;
        
        let progress = JSON.parse(localStorage.getItem('math_progress')) || {
            completedDays: [],
            scores: {}
        };

        let activeDay = 1;
        let currentProblemIndex = 0;
        let currentDayProblems = [];
        let sessionScore = 0;

        function initApp() {
            renderDashboard();
            updateHeaderStats();
        }

        function generateDayProblems(day) {
            let problems = [];
            for (let i = 1; i <= PROBLEMS_PER_DAY; i++) {
                let seed = day * 1000 + i;
                let a = (seed * 13) % 89 + 11;
                let b = (seed * 7) % 89 + 11;
                let ops = ['+', '-', '*'];
                let op = ops[(seed + day) % 3];
                
                let ans;
                if (op === '+') ans = a + b;
                else if (op === '-') ans = a - b;
                else {
                    a = (seed * 3) % 12 + 2;
                    b = (seed * 5) % 12 + 2;
                    ans = a * b;
                }
                problems.push({ q: `${a} ${op} ${b} = ?`, a: ans });
            }
            return problems;
        }

        function renderDashboard() {
            const grid = document.getElementById('days-grid');
            grid.innerHTML = '';

            let allCompleted = progress.completedDays.length === TOTAL_DAYS;

            if (allCompleted) {
                let banner = document.createElement('div');
                banner.className = 'col-span-full bg-gradient-to-r from-blue-950 via-blue-900 to-amber-950 border border-amber-500/40 p-6 rounded-2xl flex items-center justify-between mb-4 shadow-xl';
                banner.innerHTML = `
                    <div>
                        <h3 class='text-xl font-bold text-white mb-1'><i class="fa-solid fa-medal text-amber-400 mr-2"></i>Curriculum Completed!</h3>
                        <p class='text-blue-200 text-sm'>You have successfully conquered all 1,000 problems across 10 days.</p>
                    </div>
                    <button onclick="showCertificate()" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-6 py-3 rounded-xl shadow-lg transition">
                        View Certificate
                    </button>
                `;
                grid.appendChild(banner);
            }

            for (let d = 1; d <= TOTAL_DAYS; d++) {
                let isCompleted = progress.completedDays.includes(d);
                let card = document.createElement('div');
                card.className = `bg-[#0b132b] border rounded-2xl p-5 flex flex-col justify-between transition relative overflow-hidden ${isCompleted ? 'border-amber-500/50 bg-blue-950/30' : 'border-blue-900/40 hover:border-amber-500/40'}`;
                
                card.innerHTML = `
                    <div>
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-xs font-bold text-blue-300 uppercase tracking-wider">Day ${d}</span>
                            ${isCompleted ? '<span class="text-amber-400 text-xs bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30 font-semibold"><i class="fa-solid fa-check mr-1"></i>Done</span>' : '<span class="text-blue-400/60 text-xs">100 Problems</span>'}
                        </div>
                        <h4 class="text-lg font-bold text-white mb-1">Module ${d}</h4>
                        <p class="text-xs text-blue-300/70 mb-6">${isCompleted ? 'Score: 100/100' : 'Pending completion'}</p>
                    </div>
                    <button onclick="startDay(${d})" class="w-full py-2.5 rounded-xl font-semibold text-sm transition ${isCompleted ? 'bg-blue-900/60 text-blue-200 hover:bg-blue-800' : 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 hover:from-amber-400 hover:to-amber-500 shadow-md shadow-amber-500/20'}">
                        ${isCompleted ? 'Review / Retake' : 'Start Day'}
                    </button>
                `;
                grid.appendChild(card);
            }
        }

        function updateHeaderStats() {
            let totalSolved = Object.values(progress.scores).reduce((a, b) => a + b, 0);
            if (totalSolved > 0 || progress.completedDays.length > 0) {
                document.getElementById('user-stats').classList.remove('hidden');
                document.getElementById('total-score').innerText = totalSolved;
            }
        }

        function startDay(day) {
            activeDay = day;
            currentProblemIndex = 0;
            sessionScore = 0;
            currentDayProblems = generateDayProblems(day);
            
            document.getElementById('view-dashboard').classList.add('hidden');
            document.getElementById('view-quiz').classList.remove('hidden');
            document.getElementById('quiz-day-tag').innerText = `Day ${day} Curriculum`;
            
            loadProblem();
        }

        function loadProblem() {
            if (currentProblemIndex >= PROBLEMS_PER_DAY) {
                finishDay();
                return;
            }
            document.getElementById('quiz-progress-text').innerText = `Problem ${currentProblemIndex + 1} of ${PROBLEMS_PER_DAY}`;
            document.getElementById('question-box').innerText = currentDayProblems[currentProblemIndex].q;
            let inputField = document.getElementById('answer-input');
            inputField.value = '';
            inputField.focus();
        }

        function submitAnswer() {
            let inputField = document.getElementById('answer-input');
            let val = parseInt(inputField.value);
            
            if (isNaN(val)) return;

            let correctVal = currentDayProblems[currentProblemIndex].a;
            if (val === correctVal) {
                sessionScore++;
            }

            currentProblemIndex++;
            loadProblem();
        }

        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !document.getElementById('view-quiz').classList.contains('hidden')) {
                submitAnswer();
            }
        });

        function finishDay() {
            progress.scores[activeDay] = sessionScore;
            if (!progress.completedDays.includes(activeDay)) {
                progress.completedDays.push(activeDay);
                progress.completedDays.sort((a,b)=>a-b);
            }
            localStorage.setItem('math_progress', JSON.stringify(progress));

            alert(`Day ${activeDay} Completed! You scored ${sessionScore}/100.`);
            returnToDashboard();
        }

        function returnToDashboard() {
            document.getElementById('view-quiz').classList.add('hidden');
            document.getElementById('view-certificate').classList.add('hidden');
            document.getElementById('view-dashboard').classList.remove('hidden');
            renderDashboard();
            updateHeaderStats();
        }

        function showCertificate() {
            document.getElementById('view-dashboard').classList.add('hidden');
            document.getElementById('view-certificate').classList.remove('hidden');
            
            let todayStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('cert-date').innerText = todayStr;
        }

        window.onload = initApp;
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
