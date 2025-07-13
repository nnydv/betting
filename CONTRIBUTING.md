# Contributing to Football Match Prediction System

Thank you for your interest in contributing to the Football Match Prediction System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists in our [Issue Tracker](https://github.com/your-username/football-prediction-system/issues)
2. Use our issue templates when available
3. Provide as much detail as possible

**Bug Reports should include:**
- Clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs if applicable

**Feature Requests should include:**
- Clear description of the proposed feature
- Use case and motivation
- Possible implementation approach
- Any relevant examples or mockups

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/football-prediction-system.git
   cd football-prediction-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest tests/
   ```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow our coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=src tests/
   
   # Run linting
   flake8 src/
   black --check src/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new prediction feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Use our PR template
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all checks pass

## 📝 Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Use descriptive variable names
prediction_accuracy = calculate_accuracy(y_true, y_pred)

# Add type hints
def train_model(X: pd.DataFrame, y: pd.Series) -> bool:
    """Train the machine learning model."""
    pass

# Use docstrings for functions and classes
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw football match data.
    
    Args:
        df: Raw match data DataFrame
        
    Returns:
        Preprocessed DataFrame
        
    Raises:
        ValueError: If required columns are missing
    """
    pass
```

### Code Organization

```
src/
├── data/
│   ├── __init__.py
│   ├── scraper.py          # Data scraping functionality
│   └── cleaner.py          # Data cleaning functionality
├── models/
│   ├── __init__.py
│   ├── trainer.py          # Model training
│   └── predictor.py        # Model prediction
├── web/
│   ├── __init__.py
│   ├── app.py             # Flask application
│   └── templates/         # HTML templates
└── utils/
    ├── __init__.py
    ├── config.py          # Configuration management
    └── logger.py          # Logging utilities
```

### Testing Guidelines

- Write unit tests for all new functions
- Use meaningful test names
- Test both success and failure cases
- Mock external dependencies

```python
def test_data_cleaner_removes_invalid_goals():
    """Test that cleaner removes rows with negative goals."""
    # Arrange
    df = pd.DataFrame({
        'home_goals': [2, -1, 3],
        'away_goals': [1, 2, 0],
        'result': ['H', 'A', 'H']
    })
    
    # Act
    cleaner = FootballDataCleaner()
    result = cleaner.clean_data(df)
    
    # Assert
    assert len(result) == 2
    assert all(result['home_goals'] >= 0)
    assert all(result['away_goals'] >= 0)
```

## 📋 Pull Request Guidelines

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows our style guidelines
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes
- [ ] No merge conflicts

### Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(model): add hyperparameter tuning for XGBoost
fix(scraper): handle network timeouts properly
docs(readme): update installation instructions
test(cleaner): add tests for data validation
```

### Review Process

1. **Automated Checks**: All PRs must pass automated tests and linting
2. **Code Review**: At least one maintainer will review your code
3. **Testing**: New features should include comprehensive tests
4. **Documentation**: Update relevant documentation

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on

## 🎯 Areas for Contribution

We welcome contributions in these areas:

### 🔧 **Technical Improvements**
- Model performance optimization
- New feature engineering techniques
- Better hyperparameter tuning strategies
- Code performance improvements

### 📊 **Data Science**
- New prediction models
- Advanced feature engineering
- Model interpretation techniques
- Data visualization improvements

### 🌐 **Web Interface**
- UI/UX improvements
- New visualization features
- Mobile responsiveness
- API enhancements

### 📚 **Documentation**
- Tutorial improvements
- Code examples
- Architecture documentation
- User guides

### 🧪 **Testing**
- Unit test coverage
- Integration tests
- Performance benchmarks
- Edge case testing

## 💡 Development Tips

1. **Start Small**: Begin with small, focused changes
2. **Ask Questions**: Don't hesitate to ask for clarification
3. **Stay Updated**: Keep your fork synchronized with the main repository
4. **Be Patient**: Code review takes time, especially for larger changes

## 📞 Getting Help

If you need help:

1. Check our [Documentation](README.md)
2. Search existing [Issues](https://github.com/your-username/football-prediction-system/issues)
3. Join our community discussions
4. Contact maintainers directly

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mentions for outstanding contributions

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the Football Match Prediction System! 🚀⚽