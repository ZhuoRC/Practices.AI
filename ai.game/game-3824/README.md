# 24 Point Math Puzzle Game 🎯

A challenging and engaging math puzzle game where players use four numbers with basic arithmetic operations to reach exactly 24. Perfect for all ages and skill levels!

## 🎮 Game Features

### Core Gameplay
- **Classic 24 Point Rules**: Use 4 numbers with +, -, ×, ÷ to get 24
- **Smart Expression Builder**: Visual expression building with real-time calculation
- **Auto-Calculation**: See results instantly as you build your expression
- **Parentheses Support**: Use parentheses to create complex calculations

### Difficulty Levels
- **🟢 Easy**: Numbers 1-6, multiple solutions available
- **🟡 Medium**: Numbers 1-9, moderate challenge
- **🔴 Hard**: Numbers 1-13, expert difficulty

### Interactive Features
- **Touch-Friendly Design**: Optimized for tablets and mobile devices
- **Card Selection**: Click to select/deselect numbers
- **Smart Validation**: Prevents invalid operations
- **Hint System**: Get help when stuck (costs points)
- **Undo Function**: Correct mistakes easily

### Visual Design
- **Modern UI**: Clean, gradient-based design
- **Smooth Animations**: Card flips, button interactions
- **Celebration Effects**: Confetti animation on success
- **Responsive Layout**: Works perfectly on all screen sizes
- **iPad Optimized**: Special layout for iPad devices

## 🎯 How to Play

### Basic Rules
1. **Use all 4 numbers** exactly once each
2. **Use only** +, -, ×, ÷ operations
3. **Use parentheses** as needed for order of operations
4. **Reach exactly 24** to win

### Controls
- **Click cards** to select numbers
- **Click operators** (+, -, ×, ÷) to add operations
- **Click "Calculate"** to check your answer
- **Click "Clear"** to start over
- **Click "Undo"** to remove last item
- **Click "New Game"** for new numbers

### Keyboard Shortcuts
- **Enter**: Calculate result
- **Escape**: Clear expression
- **Ctrl+Z**: Undo last action
- **N**: New game
- **H**: Show hint

## 🏆 Scoring System

### Points
- **Base Points**: 10 points per successful solution
- **Level Multiplier**: Higher levels = more points
- **Streak Bonus**: Consecutive wins build streak
- **Hint Penalty**: -5 points for using hints

### Statistics
- **Level**: Current difficulty progression
- **Score**: Total accumulated points
- **Streak**: Current consecutive wins
- **Best Streak**: Personal record
- **Success Rate**: Percentage of completed games

## 🛠️ Technical Features

### Frontend Technologies
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with animations
- **Vanilla JavaScript**: No frameworks required
- **Local Storage**: Persistent game statistics

### Advanced Features
- **Solution Validator**: Checks mathematical expressions
- **Expression Parser**: Safe mathematical evaluation
- **Responsive Design**: Mobile-first approach
- **Touch Optimization**: Large touch targets for tablets
- **Accessibility**: Keyboard navigation support

### Browser Compatibility
- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile Safari (iOS)
- ✅ Chrome Mobile (Android)

## 📱 Device Optimization

### iPad Features
- **Compact Layout**: Fits entire game on iPad screen
- **Touch Targets**: Minimum 44px touch targets
- **Landscape Mode**: Special horizontal layout
- **Portrait Mode**: Optimized vertical layout

### Mobile Support
- **Responsive Design**: Adapts to all screen sizes
- **Touch Gestures**: Intuitive touch interactions
- **Performance**: Optimized for mobile devices
- **No Scroll**: Everything fits on one screen

## 🎨 Design System

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success**: Green (#4caf50)
- **Error**: Red (#f44336)
- **Warning**: Orange (#ff9800)
- **Info**: Blue (#2196f3)

### Typography
- **Headings**: Bold, impactful
- **Body**: Clean, readable
- **Numbers**: Large, clear display
- **Cards**: Playing card aesthetic

### Animations
- **Card Flip**: 0.6s smooth rotation
- **Button Press**: 0.2s scale effect
- **Celebration**: 3s confetti animation
- **Shake**: 0.5s error feedback

## 🚀 Getting Started

### Prerequisites
- Modern web browser
- No additional software required

### Installation & Running
1. **Clone/Download** the project files
2. **Navigate** to the project directory
3. **Start** a local server:
   ```bash
   # Using Python
   python -m http.server 5100
   
   # Using Node.js
   npx http-server -p 5100
   
   # Using PHP
   php -S localhost:5100
   ```
4. **Open** browser to `http://localhost:5100`

### Alternative Methods
- **Live Server**: Use VS Code Live Server extension
- **GitHub Pages**: Deploy to GitHub Pages
- **Netlify**: Drag-and-drop deployment

## 📁 Project Structure

```
game-3824/
├── index.html          # Main HTML file
├── css/
│   └── style.css      # Styling and animations
├── js/
│   └── game.js        # Game logic and interactions
└── README.md          # Documentation (this file)
```

## 🎮 Game Logic

### Expression Building
- **Token System**: Numbers and operators as tokens
- **Validation**: Prevents invalid expressions
- **Real-time Updates**: Live calculation display
- **Visual Feedback**: Selected states and usage tracking

### Solution Checking
- **Mathematical Evaluation**: Safe expression parsing
- **Precision Handling**: Floating-point comparison
- **Error Handling**: Graceful error management
- **Success Detection**: Automatic win detection

### Number Generation
- **Difficulty-Based**: Range varies by difficulty
- **Solution Guarantee**: Ensures solvable combinations
- **Fallback System**: Known solvable patterns
- **Variety**: Prevents repetitive puzzles

## 🔧 Customization

### Difficulty Settings
```javascript
difficultySettings: {
    easy: { minNumber: 1, maxNumber: 6, solutions: 3 },
    medium: { minNumber: 1, maxNumber: 9, solutions: 2 },
    hard: { minNumber: 1, maxNumber: 13, solutions: 1 }
}
```

### Styling Customization
- **Colors**: Modify CSS variables
- **Animations**: Adjust timing functions
- **Layout**: Grid and flexbox properties
- **Typography**: Font families and sizes

### Game Rules
- **Target Number**: Change from 24 to any number
- **Operations**: Add or remove operators
- **Card Count**: Use different numbers of cards
- **Scoring**: Customize point system

## 🌟 Educational Benefits

### Math Skills
- **Arithmetic Operations**: +, -, ×, ÷ practice
- **Order of Operations**: Parentheses and precedence
- **Problem Solving**: Logical thinking
- **Mental Math**: Quick calculation skills

### Cognitive Skills
- **Pattern Recognition**: Number relationships
- **Strategic Thinking**: Planning expressions
- **Memory**: Remembering previous attempts
- **Concentration**: Focus on the goal

## 📈 Future Enhancements

### Planned Features
- **Multiplayer Mode**: Compete with friends
- **Time Attack**: Speed-based challenges
- **Leaderboards**: Global rankings
- **Achievements**: Unlockable badges
- **Custom Themes**: Different visual styles

### Technical Improvements
- **PWA Support**: Offline play capability
- **Sound Effects**: Audio feedback
- **Haptic Feedback**: Vibration on mobile
- **Cloud Save**: Cross-device synchronization

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

### Code Guidelines
- **Clean Code**: Readable and maintainable
- **Comments**: Explain complex logic
- **Consistency**: Follow existing patterns
- **Performance**: Optimize for all devices

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **24 Point Game**: Classic mathematical puzzle concept
- **Modern Web Standards**: HTML5, CSS3, ES6+
- **Responsive Design**: Mobile-first approach
- **Touch Optimization**: iPad and tablet support

---

**Enjoy the 24 Point Math Puzzle Game! 🎯🧮✨**

**Made with ❤️ for math enthusiasts and puzzle lovers!**
