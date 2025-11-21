class Game24 {
    constructor() {
        this.cards = [];
        this.selectedCards = new Set();
        this.expression = [];
        this.currentNumbers = [];
        this.usedCards = new Set();
        
        // Game statistics
        this.level = 1;
        this.score = 0;
        this.streak = 0;
        this.bestStreak = 0;
        this.totalGames = 0;
        this.successfulGames = 0;
        
        // Difficulty settings - expanded ranges to avoid duplicates
        this.difficulty = 'medium';
        this.difficultySettings = {
            easy: { minNumber: 1, maxNumber: 8, solutions: 3 }, // Expanded from 1-6 to 1-8
            medium: { minNumber: 1, maxNumber: 9, solutions: 2 },
            hard: { minNumber: 1, maxNumber: 13, solutions: 1 }
        };
        
        this.initializeElements();
        this.loadGameData();
        this.bindEvents();
        this.startNewGame();
    }

    initializeElements() {
        // Card elements - new horizontal layout
        this.cardElements = document.querySelectorAll('.card');
        this.cardsContainer = document.querySelector('.cards-container-horizontal');
        
        // Operator buttons - new large buttons
        this.operatorBtns = document.querySelectorAll('.operator-btn-large');
        
        // Display elements - new large expression display
        this.expressionDisplay = document.getElementById('expression');
        this.resultDisplay = document.getElementById('result');
        this.feedbackContainer = document.getElementById('feedback');
        
        // Top feedback and score displays
        this.topFeedbackContainer = document.getElementById('top-feedback');
        this.topScoreDisplay = document.getElementById('top-score');
        
        // Control buttons - new icon buttons
        this.calculateBtn = null; // Removed - no calculate button needed
        this.clearBtn = document.getElementById('clear-btn');
        this.undoBtn = document.getElementById('undo-btn');
        this.hintBtn = document.getElementById('hint-btn-icon'); // New icon button
        this.newGameBtn = document.getElementById('new-game-btn');
        
        // Statistics display
        this.levelDisplay = document.getElementById('level');
        this.scoreDisplay = document.getElementById('score');
        this.streakDisplay = document.getElementById('streak');
        this.bestStreakDisplay = document.getElementById('best-streak');
        this.totalGamesDisplay = document.getElementById('total-games');
        this.successRateDisplay = document.getElementById('success-rate');
        
        // Difficulty selector
        this.difficultySelect = document.getElementById('difficulty');
        
        // Modal
        this.hintModal = document.getElementById('hint-modal');
        this.hintText = document.getElementById('hint-text');
    }

    bindEvents() {
        // Card click events
        this.cardElements.forEach((card, index) => {
            card.addEventListener('click', () => this.selectCard(index));
        });
        
        // Operator click events
        this.operatorBtns.forEach(btn => {
            btn.addEventListener('click', () => this.selectOperator(btn.dataset.op));
        });
        
        // Control button events - removed calculate button
        this.clearBtn.addEventListener('click', () => this.clearExpression());
        this.undoBtn.addEventListener('click', () => this.undo());
        this.hintBtn.addEventListener('click', () => this.showHint());
        this.newGameBtn.addEventListener('click', () => this.startNewGame());
        
        // Difficulty selector event
        this.difficultySelect.addEventListener('change', (e) => {
            this.difficulty = e.target.value;
            this.startNewGame();
        });
        
        // Keyboard shortcuts - removed Enter key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.clearExpression();
            if (e.ctrlKey && e.key === 'z') this.undo();
            if (e.key === 'n' || e.key === 'N') this.startNewGame();
            if (e.key === 'h' || e.key === 'H') this.showHint();
        });
    }

    startNewGame() {
        // Reset game state
        this.selectedCards.clear();
        this.expression = [];
        this.usedCards.clear();
        
        // Generate new numbers
        this.generateNumbers();
        
        // Update display
        this.updateCardsDisplay();
        this.updateExpression();
        this.clearFeedback();
        this.updateStats();
        
        // Add animation effects
        this.cardElements.forEach((card, index) => {
            card.classList.add('flip');
            setTimeout(() => card.classList.remove('flip'), 600);
        });
    }

    generateNumbers() {
        const settings = this.difficultySettings[this.difficulty];
        const numbers = [];
        
        // Generate truly random numbers with better randomness and avoid duplicates
        let attempts = 0;
        let validSolution = false;
        
        do {
            numbers.length = 0;
            
            // Generate 4 random numbers with better distribution
            // Create a pool of available numbers
            const availableNumbers = [];
            for (let i = settings.minNumber; i <= settings.maxNumber; i++) {
                availableNumbers.push(i);
            }
            
            // Shuffle the available numbers
            for (let i = availableNumbers.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [availableNumbers[i], availableNumbers[j]] = [availableNumbers[j], availableNumbers[i]];
            }
            
            // Try to pick 4 unique numbers first
            if (availableNumbers.length >= 4) {
                for (let i = 0; i < 4; i++) {
                    numbers.push(availableNumbers[i]);
                }
            } else {
                // If range is too small, allow some duplicates but minimize them
                for (let i = 0; i < 4; i++) {
                    const random1 = Math.random();
                    const random2 = Math.random();
                    const finalRandom = (random1 + random2) / 2;
                    numbers.push(Math.floor(finalRandom * (settings.maxNumber - settings.minNumber + 1)) + settings.minNumber);
                }
            }
            
            attempts++;
            
            // Check if this combination has a solution
            const solutions = this.hasSolution(numbers);
            validSolution = solutions.length > 0;
            
            // Prevent infinite loop - if no valid solution found after many attempts, use fallback
            if (attempts > 200) {
                // Use multiple fallback combinations for more variety
                const fallbackSets = [
                    [3, 8, 1, 1], [4, 6, 2, 1], [2, 12, 2, 1], 
                    [3, 3, 8, 1], [4, 4, 3, 2], [6, 4, 1, 1],
                    [2, 3, 4, 6], [1, 5, 4, 6], [2, 2, 6, 6],
                    [3, 4, 2, 4], [5, 5, 1, 5], [2, 8, 3, 1],
                    [4, 3, 2, 6], [1, 8, 3, 3], [6, 2, 2, 6],
                    [1, 2, 3, 8], [1, 4, 5, 6], [2, 3, 8, 1]
                ];
                const randomFallback = fallbackSets[Math.floor(Math.random() * fallbackSets.length)];
                numbers.splice(0, 4, ...randomFallback);
                console.log('Used fallback combination:', randomFallback);
                break;
            }
        } while (!validSolution);
        
        // Shuffle numbers to randomize their positions
        for (let i = numbers.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [numbers[i], numbers[j]] = [numbers[j], numbers[i]];
        }
        
        this.currentNumbers = numbers;
        this.currentSolution = this.hasSolution(numbers)[0];
        
        console.log('Generated numbers:', numbers, 'Solution:', this.currentSolution, 'Attempts:', attempts);
    }

    hasSolution(numbers) {
        // Simplified solution finder for 24 point game
        const solutions = [];
        const [a, b, c, d] = numbers;
        
        // Check common patterns
        if (Math.abs(a * b * c * d - 24) < 0.001) {
            solutions.push(`${a}×${b}×${c}×${d}`);
        }
        
        if (Math.abs(a * b * (c + d) - 24) < 0.001) {
            solutions.push(`${a}×${b}×(${c}+${d})`);
        }
        
        if (Math.abs((a + b) * (c + d) - 24) < 0.001) {
            solutions.push(`(${a}+${b})×(${c}+${d})`);
        }
        
        if (Math.abs(a * b + c * d - 24) < 0.001) {
            solutions.push(`${a}×${b}+${c}×${d}`);
        }
        
        if (Math.abs((a + b + c) * d - 24) < 0.001) {
            solutions.push(`(${a}+${b}+${c})×${d}`);
        }
        
        if (Math.abs(a * b * c - d - 24) < 0.001) {
            solutions.push(`${a}×${b}×${c}-${d}`);
        }
        
        // Check division patterns
        if (b !== 0 && Math.abs(a / b * c * d - 24) < 0.001) {
            solutions.push(`${a}÷${b}×${c}×${d}`);
        }
        
        if (c !== 0 && Math.abs(a * b / c * d - 24) < 0.001) {
            solutions.push(`${a}×${b}÷${c}×${d}`);
        }
        
        // Check more complex combinations
        try {
            const allPermutations = this.getPermutations(numbers);
            for (const perm of allPermutations) {
                const result = this.tryAllOperations(perm);
                if (result.length > 0) {
                    solutions.push(...result);
                    break;
                }
            }
        } catch (e) {
            console.log('Solution finder error:', e);
        }
        
        return solutions.slice(0, 5);
    }

    getPermutations(arr) {
        if (arr.length <= 1) return [arr];
        const result = [];
        for (let i = 0; i < arr.length; i++) {
            const current = arr[i];
            const remaining = [...arr.slice(0, i), ...arr.slice(i + 1)];
            const perms = this.getPermutations(remaining);
            for (const perm of perms) {
                result.push([current, ...perm]);
            }
        }
        return result;
    }

    tryAllOperations(numbers) {
        const solutions = [];
        const [a, b, c, d] = numbers;
        
        // Check 3×8=24 pattern
        if (Math.abs(a * b - 24) < 0.001 && c === 1 && d === 1) {
            solutions.push(`${a}×${b}×${c}×${d}`);
        }
        
        return solutions;
    }

    selectCard(index) {
        const card = this.cardElements[index];
        const value = this.currentNumbers[index];
        
        if (this.usedCards.has(index)) {
            this.showFeedback('This number has already been used!', 'warning');
            return;
        }
        
        if (this.selectedCards.has(index)) {
            // Cannot re-select already selected card
            this.showFeedback('This number is already selected!', 'warning');
            return;
        }
        
        // Check if last selected item was a number (prevent consecutive numbers)
        const lastItem = this.expression[this.expression.length - 1];
        if (lastItem && lastItem.type === 'number') {
            // Remove previously selected number and its card selection
            const previousCardIndex = lastItem.cardIndex;
            this.selectedCards.delete(previousCardIndex);
            this.cardElements[previousCardIndex].classList.remove('selected');
            this.expression.pop();
        }
        
        // Select new card
        this.selectedCards.add(index);
        card.classList.add('selected');
        this.expression.push({ type: 'number', value, cardIndex: index });
        
        this.updateExpression();
        this.autoCalculate();
    }

    removeNumberFromExpression(value) {
        // Remove last occurrence of this number from expression
        for (let i = this.expression.length - 1; i >= 0; i--) {
            if (this.expression[i].type === 'number' && this.expression[i].value === value) {
                this.expression.splice(i, 1);
                break;
            }
        }
    }

    selectOperator(operator) {
        // Check if expression can add operator
        const lastItem = this.expression[this.expression.length - 1];
        
        // For opening parenthesis, allow at any position
        if (operator === '(') {
            // Allow opening parenthesis anywhere
            // If last item is a number or closing parenthesis, insert multiplication implicitly
            if (lastItem && (lastItem.type === 'number' || lastItem.value === ')')) {
                this.expression.push({ type: 'operator', value: '*' });
            }
        } else if (operator === ')') {
            // For closing parenthesis, check if we have valid expression structure
            if (this.expression.length === 0) {
                this.showFeedback('Please build expression first!', 'warning');
                return;
            }
            
            // Count open parentheses to ensure we can close one
            let openCount = 0;
            for (const item of this.expression) {
                if (item.value === '(') openCount++;
                if (item.value === ')') openCount--;
            }
            
            if (openCount <= 0) {
                this.showFeedback('No matching opening parenthesis!', 'warning');
                return;
            }
            
            // Don't allow closing parenthesis right after operator (except opening parenthesis)
            if (lastItem && lastItem.type === 'operator' && lastItem.value !== '(') {
                this.showFeedback('Cannot close parenthesis after operator!', 'warning');
                return;
            }
        } else {
            // For other operators, check standard rules
            if (lastItem && lastItem.type === 'operator') {
                this.showFeedback('Cannot add consecutive operators!', 'warning');
                return;
            }
        }
        
        this.expression.push({ type: 'operator', value: operator });
        this.updateExpression();
        this.autoCalculate();
    }

    updateExpression() {
        if (this.expression.length === 0) {
            this.expressionDisplay.innerHTML = '<span class="placeholder">Select numbers and operators to build expression</span>';
            this.resultDisplay.textContent = '?';
            return;
        }
        
        let html = '';
        let usedNumbers = new Set();
        
        for (const item of this.expression) {
            if (item.type === 'number') {
                html += `<span class="token number-token">${item.value}</span>`;
                usedNumbers.add(item.cardIndex);
            } else {
                html += `<span class="token operator-token">${this.getOperatorSymbol(item.value)}</span>`;
            }
        }
        
        this.expressionDisplay.innerHTML = html;
        
        // Update used cards status
        this.cardElements.forEach((card, index) => {
            if (usedNumbers.has(index)) {
                card.classList.add('used');
                this.usedCards.add(index);
            } else if (!this.selectedCards.has(index)) {
                card.classList.remove('used');
                this.usedCards.delete(index);
            }
        });
    }

    getOperatorSymbol(op) {
        const symbols = {
            '+': '+',
            '-': '−',
            '*': '×',
            '/': '÷',
            '(': '(',
            ')': ')'
        };
        return symbols[op] || op;
    }

    autoCalculate() {
        try {
            const result = this.evaluateExpression();
            if (result !== null) {
                // Check if result is an integer and display accordingly
                if (Number.isInteger(result)) {
                    this.resultDisplay.textContent = result.toString();
                } else {
                    this.resultDisplay.textContent = result.toFixed(2);
                }
                
                // If result is 24, show success
                if (Math.abs(result - 24) < 0.001 && this.usedCards.size === 4) {
                    this.handleSuccess();
                }
            } else {
                this.resultDisplay.textContent = '?';
            }
        } catch (e) {
            this.resultDisplay.textContent = '?';
        }
    }

    calculate() {
        // Manual calculation - can be called if needed
        if (this.usedCards.size !== 4) {
            this.showFeedback('Please use all 4 numbers!', 'warning');
            return;
        }
        
        try {
            const result = this.evaluateExpression();
            if (result === null) {
                this.showFeedback('Expression is incomplete!', 'error');
                return;
            }
            
            if (Math.abs(result - 24) < 0.001) {
                this.handleSuccess();
            } else {
                this.showFeedback(`Result is ${result}, not 24! Try again!`, 'error');
                this.streak = 0;
                this.updateStats();
                this.shakeElement(this.expressionDisplay);
            }
        } catch (e) {
            this.showFeedback('Expression error, please check!', 'error');
        }
    }

    evaluateExpression() {
        if (this.expression.length === 0) return null;
        
        // Build calculation expression
        let expr = '';
        let numberCount = 0;
        
        for (const item of this.expression) {
            if (item.type === 'number') {
                expr += item.value;
                numberCount++;
            } else {
                expr += item.value;
            }
        }
        
        if (numberCount !== 4) return null;
        
        try {
            // Use Function constructor to safely evaluate expression
            const result = new Function('return ' + expr)();
            return result;
        } catch (e) {
            return null;
        }
    }

    handleSuccess() {
        this.score += 10 * this.level;
        this.streak++;
        this.level++;
        this.totalGames++;
        this.successfulGames++;
        
        if (this.streak > this.bestStreak) {
            this.bestStreak = this.streak;
        }
        
        this.showFeedback(`🎉 Excellent! You got 24! Earned ${10 * (this.level - 1)} points!`, 'success');
        this.updateStats();
        this.saveGameData();
        this.triggerCelebration();
        
        // Remove auto-start new game - stay on success page
        // setTimeout(() => {
        //     this.startNewGame();
        // }, 2000);
    }

    clearExpression() {
        this.expression = [];
        this.selectedCards.clear();
        this.usedCards.clear();
        
        this.cardElements.forEach(card => {
            card.classList.remove('selected', 'used');
        });
        
        this.updateExpression();
        this.clearFeedback();
    }

    undo() {
        if (this.expression.length === 0) return;
        
        const lastItem = this.expression.pop();
        
        if (lastItem.type === 'number') {
            this.selectedCards.delete(lastItem.cardIndex);
            this.cardElements[lastItem.cardIndex].classList.remove('selected');
        }
        
        this.updateExpression();
        this.autoCalculate();
    }

    showHint() {
        if (!this.currentSolution) {
            this.showFeedback('No hint available!', 'info');
            return;
        }
        
        this.hintText.textContent = `Hint: Try ${this.currentSolution}`;
        this.hintModal.style.display = 'block';
        
        // Deduct points
        this.score = Math.max(0, this.score - 5);
        this.updateStats();
    }

    clearFeedback() {
        this.feedbackContainer.innerHTML = '';
        this.topFeedbackContainer.innerHTML = '';
    }

    showFeedback(message, type = 'info') {
        // Show feedback at top
        const topFeedbackMessage = document.createElement('div');
        topFeedbackMessage.className = `top-feedback-message ${type}`;
        topFeedbackMessage.textContent = message;
        
        this.topFeedbackContainer.innerHTML = '';
        this.topFeedbackContainer.appendChild(topFeedbackMessage);
        
        // Auto clear after 3 seconds
        setTimeout(() => {
            if (this.topFeedbackContainer.contains(topFeedbackMessage)) {
                topFeedbackMessage.remove();
            }
        }, 3000);
    }

    updateStats() {
        this.levelDisplay.textContent = this.level;
        this.scoreDisplay.textContent = this.score;
        this.streakDisplay.textContent = this.streak;
        this.bestStreakDisplay.textContent = this.bestStreak;
        this.totalGamesDisplay.textContent = this.totalGames;
        
        // Update top score display
        this.topScoreDisplay.textContent = this.score;
        
        const successRate = this.totalGames > 0 ? 
            Math.round((this.successfulGames / this.totalGames) * 100) : 0;
        this.successRateDisplay.textContent = successRate + '%';
        
        // Add animation for number changes
        [this.levelDisplay, this.scoreDisplay, this.streakDisplay].forEach(el => {
            el.style.transform = 'scale(1.2)';
            setTimeout(() => {
                el.style.transform = 'scale(1)';
            }, 200);
        });
        
        // Add animation for top score
        this.topScoreDisplay.style.transform = 'scale(1.2)';
        setTimeout(() => {
            this.topScoreDisplay.style.transform = 'scale(1)';
        }, 200);
    }

    updateCardsDisplay() {
        const suits = ['♠', '♥', '♣', '♦'];
        
        this.cardElements.forEach((card, index) => {
            const numberEl = card.querySelector('.number');
            const suitEl = card.querySelector('.suit');
            
            numberEl.textContent = this.currentNumbers[index];
            suitEl.textContent = suits[index];
            
            // Reset card state
            card.classList.remove('selected', 'used');
            card.dataset.value = this.currentNumbers[index];
        });
    }

    triggerCelebration() {
        const celebration = document.createElement('div');
        celebration.className = 'celebration';
        
        const colors = ['#667eea', '#764ba2', '#4caf50', '#ff6b6b', '#ffd93d', '#6bcf7f'];
        
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
            celebration.appendChild(confetti);
        }
        
        document.body.appendChild(celebration);
        
        setTimeout(() => {
            if (document.body.contains(celebration)) {
                document.body.removeChild(celebration);
            }
        }, 4000);
        
        // Play success sound
        this.playSuccessSound();
    }

    playSuccessSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
            oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (e) {
            console.log('Sound playback failed:', e);
        }
    }

    shakeElement(element) {
        element.style.animation = 'shake 0.5s';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    }

    saveGameData() {
        const gameData = {
            bestStreak: this.bestStreak,
            totalGames: this.totalGames,
            successfulGames: this.successfulGames,
            level: this.level,
            score: this.score
        };
        
        localStorage.setItem('game24Data', JSON.stringify(gameData));
    }

    loadGameData() {
        try {
            const savedData = localStorage.getItem('game24Data');
            if (savedData) {
                const gameData = JSON.parse(savedData);
                this.bestStreak = gameData.bestStreak || 0;
                this.totalGames = gameData.totalGames || 0;
                this.successfulGames = gameData.successfulGames || 0;
                this.level = gameData.level || 1;
                this.score = gameData.score || 0;
            }
        } catch (e) {
            console.log('Failed to load game data:', e);
        }
    }
}

// Close hint modal
function closeHintModal() {
    document.getElementById('hint-modal').style.display = 'none';
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    const game = new Game24();
    
    // Close modal when clicking outside
    document.getElementById('hint-modal').addEventListener('click', (e) => {
        if (e.target.id === 'hint-modal') {
            closeHintModal();
        }
    });
    
    console.log('🎮 24 Point Game loaded!');
    console.log('💡 Tips:');
    console.log('- Escape: Clear expression');
    console.log('- Ctrl+Z: Undo');
    console.log('- N: New game');
    console.log('- H: Show hint');
    console.log('- Auto-calculate enabled - no need for Enter key');
    console.log('- Free parenthesis input allowed');
    console.log('- Success page stays on screen - no auto new game');
    console.log('- Integer display for whole numbers');
    console.log('- New number selection logic: no consecutive numbers, replace previous selection');
    console.log('- Success messages appear at top');
    console.log('- Score displayed in top-right corner');
    console.log('- Easy difficulty now uses 1-8 range to reduce duplicates');
});
