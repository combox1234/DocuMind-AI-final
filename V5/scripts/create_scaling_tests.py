#!/usr/bin/env python3
"""Create comprehensive test files for scaled classification validation"""

import os
from pathlib import Path

# Create test files directory
BASE_DIR = Path(__file__).parent.parent
test_dir = BASE_DIR / "data/incoming/test_scaling"
test_dir.mkdir(parents=True, exist_ok=True)

test_files = {
    "DataScience_Analysis.txt": """
    Data Science Project Report
    
    This project uses numpy, pandas, and scikit-learn for machine learning classification.
    We implement a neural network using tensorflow and pytorch for deep learning tasks.
    The model uses supervised learning with features engineered from raw data.
    We perform cross validation and calculate accuracy, precision, recall, and f1 scores.
    The confusion matrix shows good performance on the test set.
    Hyperparameter tuning with grid search improves model performance.
    We use gradient descent optimization with backpropagation for training.
    """,
    
    "Backend_API_Service.txt": """
    Backend API Development
    
    This is a nodejs express backend with route handlers and middleware.
    We use sql database queries to fetch data from postgres.
    The api endpoints follow rest architecture with proper authorization.
    Middleware handles authentication and error handling.
    Database schema design uses normalized tables with foreign keys.
    """,
    
    "Frontend_React_App.txt": """
    Frontend React Application
    
    This react application uses jsx components with hooks for state management.
    We manage component state using useState and useEffect hooks.
    Props are passed from parent to child components for data flow.
    CSS styling is applied with responsive design.
    DOM manipulation is done through react reconciliation.
    """,
    
    "UAV_Technology.txt": """
    Unmanned Aerial Vehicle Project
    
    This project develops a UAV drone with quadcopter design.
    The hexacopter variant provides better stability for aerial missions.
    Flight path optimization uses algorithms to minimize energy consumption.
    The drone uses robotics principles for autonomous navigation.
    Sensors collect data during flight for research purposes.
    """,
    
    "Algorithms_DataStructures.txt": """
    Algorithms and Data Structures
    
    This covers sorting algorithms like quicksort and mergesort.
    Binary tree traversal methods: inorder, preorder, postorder.
    Graph algorithms: dijkstra, bfs, dfs for shortest path.
    Big O complexity analysis for time and space optimization.
    Recursion patterns for divide and conquer algorithms.
    """,
    
    "Finance_Budget_Report.txt": """
    Quarterly Budget Report
    
    Total revenue for this quarter: $5.2M
    Operating expenses are $2.1M with maintenance costs at $300K.
    Capital expenditure approved for infrastructure upgrade.
    Balance sheet shows assets exceed liabilities.
    Cash flow analysis indicates positive operating cash flow.
    Tax depreciation reduces net taxable income by $400K.
    GAAP accounting standards applied to all financial statements.
    """,
    
    "Mathematics_Assignment.txt": """
    Calculus Assignment Solution
    
    Problem: Find the derivative of f(x) = 3x^2 + 2x + 1
    Solution uses the power rule and sum rule.
    Algebra simplification gives f'(x) = 6x + 2.
    
    Problem: Solve the quadratic equation x^2 - 5x + 6 = 0
    Using the quadratic formula: x = (5 +/- sqrt(25-24))/2
    Solutions are x = 2 and x = 3.
    
    Geometry problem: Find area of triangle with base 10 and height 8.
    Area = 0.5 * base * height = 40 square units.
    """,
    
    "College_Course_Info.txt": """
    Computer Science 301 Course Syllabus
    
    This is a bachelor degree course at the university.
    Prerequisites: CS 201 and Mathematics 201.
    Course covers algorithms, data structures, and system design.
    Grading: assignments 40%, midterm 30%, final exam 30%.
    Students receive a grade point average (GPA) contribution.
    Registration deadline is before the semester begins.
    Alumni of this course have successful careers in tech.
    """,
    
    "Company_Product_Roadmap.txt": """
    Product Development Roadmap Q4
    
    Feature releases planned: mobile app redesign, payment integration.
    Product specifications documented in requirement documents.
    Service offerings expanded to enterprise customers.
    Marketing campaign targets business development opportunities.
    Customer support team ensures 99.9% availability.
    Prototype mockups created for stakeholder review.
    Strategic initiatives align with company culture values.
    """,
}

# Create files
for filename, content in test_files.items():
    filepath = test_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filepath}")

print(f"\nTest files created in: {test_dir}")
print(f"Total files: {len(test_files)}")
