
const questionText = document.getElementById('question-text');
const optionsForm = document.getElementById('options-form');
const optionsContainer = document.getElementById('options');
const feedbackContainer = document.getElementById('feedback-container');
const feedbackText = document.getElementById('feedback-text');
const analysisText = document.getElementById('analysis-text');
const nextButton = document.getElementById('next-button');
const completionContainer = document.getElementById('completion-container');
const restartButton = document.getElementById('restart-button');
const dismissButton = document.getElementById('dismiss-button');
const progressBar = document.getElementById('progress-bar');

let currentQuestion = null;
let totalQuestions = 0;
let completedQuestions = 0;
let correctAnswers = 0;
let incorrectAnswers = 0;

async function getNextQuestion() {
    const response = await fetch('/questions');
    const data = await response.json();

    if (data.completed) {
        // show completion UI
        completionContainer.style.display = 'block';
        optionsForm.style.display = 'none';
        questionText.textContent = "Congratulations! You have completed all questions.";
        return;
    }

    currentQuestion = data;
    questionText.textContent = currentQuestion.question;
    optionsContainer.innerHTML = '';

    for (const key in currentQuestion.options) {
        const option = document.createElement('div');
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'option';
        radio.value = key;
        radio.id = key;

        const label = document.createElement('label');
        label.textContent = currentQuestion.options[key];
        label.htmlFor = key;

        option.appendChild(radio);
        option.appendChild(label);
        optionsContainer.appendChild(option);
    }

    feedbackContainer.style.display = 'none';
    optionsForm.style.display = 'block';
    // refresh stats when a new batch/question is loaded
    await fetchAndUpdateStats();
}

async function submitAnswer(event) {
    event.preventDefault();
    const selectedOption = document.querySelector('input[name="option"]:checked');

    if (!selectedOption) {
        return;
    }

    const response = await fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            question_index: currentQuestion.index,
            selected_option: selectedOption.value
        })
    });

    const data = await response.json();

    feedbackContainer.style.display = 'block';
    optionsForm.style.display = 'none';

    if (data.correct) {
        feedbackContainer.classList.remove('incorrect');
        feedbackContainer.classList.add('correct');
        feedbackText.textContent = "Correct!";
        completedQuestions++;
        correctAnswers++;
    } else {
        feedbackContainer.classList.remove('correct');
        feedbackContainer.classList.add('incorrect');
        feedbackText.textContent = "Incorrect!";
        incorrectAnswers++;
    }

    analysisText.textContent = data.analysis;
    updateProgressBar();
    // refresh stats after submission
    await fetchAndUpdateStats();
}

function updateProgressBar() {
    const progress = (completedQuestions / totalQuestions) * 100;
    progressBar.style.width = `${progress}%`;
}

nextButton.addEventListener('click', getNextQuestion);
optionsForm.addEventListener('submit', submitAnswer);

restartButton.addEventListener('click', async () => {
    try {
        const resp = await fetch('/restart', { method: 'POST' });
        const r = await resp.json();
        if (r.restarted) {
            completionContainer.style.display = 'none';
            await fetchAndUpdateStats();
            getNextQuestion();
        }
    } catch (e) {
        console.error('Failed to restart', e);
    }
});

dismissButton.addEventListener('click', () => {
    completionContainer.style.display = 'none';
});

async function getTotalQuestions() {
    const response = await fetch('/questions');
    const data = await response.json();
    totalQuestions = data.total_questions;
}

//getTotalQuestions();
getNextQuestion();

async function fetchAndUpdateStats() {
    try {
        const resp = await fetch('/stats');
        const s = await resp.json();
        document.getElementById('stat-total').textContent = s.total_questions;
        document.getElementById('stat-left').textContent = s.questions_left;
        document.getElementById('stat-correct').textContent = s.correct_answers;
        document.getElementById('stat-incorrect').textContent = s.incorrect_answers;

        // sync local counters for progress bar calculation
        totalQuestions = s.total_questions;
        completedQuestions = totalQuestions - s.questions_left;
        correctAnswers = s.correct_answers;
        incorrectAnswers = s.incorrect_answers;
        updateProgressBar();
    } catch (e) {
        console.error('Failed to fetch stats', e);
    }
}
