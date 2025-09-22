# Enhanced ARTI Curriculum Assessment Tool
# Combines curriculum parsing, AI demonstrations, and student assessment
# Suitable for both ARTI1000X (Level 1) and ARTI2000X (Level 2)
# Author: Claude Sonnet 4 (building on Grok 4's foundation)

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import re
from typing import Dict, List, Tuple, Any

class ARTICurriculumTool:
    """
    Comprehensive tool for ARTI curriculum teaching and assessment.
    Supports both theoretical understanding and practical AI implementation.
    """
    
    def __init__(self):
        self.models = {}
        self.results = {}
        self.curriculum_data = self._load_curriculum_structure()
        
    def _load_curriculum_structure(self) -> Dict[str, Any]:
        """Load ARTI curriculum structure and learning objectives."""
        return {
            "ARTI1000X": {
                "level": "Level 1 - Foundation",
                "topics": [
                    "AI Definitions and Basic Concepts",
                    "Data Quality and AI Accuracy", 
                    "Classification and Decision Trees",
                    "Supervised vs Unsupervised Learning",
                    "Ethical Implications and Bias",
                    "AI Applications in Society"
                ],
                "practical_skills": [
                    "Simple classification tasks",
                    "Basic data analysis",
                    "Decision tree interpretation",
                    "Ethical reasoning"
                ]
            },
            "ARTI2000X": {
                "level": "Level 2 - Advanced",
                "topics": [
                    "Neural Networks and Deep Learning",
                    "Advanced Applications (Healthcare, Transport)",
                    "Risk Assessment and Safety",
                    "Advanced Ethics and Regulation",
                    "AI System Design"
                ],
                "practical_skills": [
                    "Neural network implementation",
                    "Complex problem solving",
                    "System evaluation",
                    "Advanced ethical analysis"
                ]
            }
        }
    
    def demonstrate_classification(self, level: str = "ARTI1000X") -> Dict[str, Any]:
        """
        Demonstrate classification appropriate for curriculum level.
        
        Args:
            level: Either "ARTI1000X" or "ARTI2000X"
            
        Returns:
            Dictionary containing results and educational insights
        """
        print(f"\n=== {self.curriculum_data[level]['level']} Classification Demo ===")
        
        # Load and prepare data
        iris = load_iris()
        X, y = iris.data, iris.target
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        results = {
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }
        
        # Level 1: Decision Tree (focus on interpretability)
        if level == "ARTI1000X":
            dt_classifier = DecisionTreeClassifier(
                max_depth=3, 
                random_state=42,
                min_samples_split=5  # Prevent overfitting for education
            )
            dt_classifier.fit(X_train, y_train)
            dt_pred = dt_classifier.predict(X_test)
            dt_accuracy = accuracy_score(y_test, dt_pred)
            
            self.models['decision_tree'] = dt_classifier
            results["models"]["decision_tree"] = {
                "accuracy": dt_accuracy,
                "interpretable": True,
                "complexity": "Low",
                "educational_value": "High - students can follow decision paths"
            }
            
            print(f"Decision Tree Accuracy: {dt_accuracy:.3f}")
            print("Educational Note: Decision trees show clear 'if-then' rules")
            
        # Level 2: Add Neural Network (focus on performance vs interpretability)
        elif level == "ARTI2000X":
            # Decision Tree for comparison
            dt_classifier = DecisionTreeClassifier(max_depth=5, random_state=42)
            dt_classifier.fit(X_train, y_train)
            dt_pred = dt_classifier.predict(X_test)
            dt_accuracy = accuracy_score(y_test, dt_pred)
            
            # Neural Network with proper scaling
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            nn_classifier = MLPClassifier(
                hidden_layer_sizes=(10, 5),
                max_iter=1000,
                random_state=42,
                early_stopping=True
            )
            nn_classifier.fit(X_train_scaled, y_train)
            nn_pred = nn_classifier.predict(X_test_scaled)
            nn_accuracy = accuracy_score(y_test, nn_pred)
            
            self.models['decision_tree'] = dt_classifier
            self.models['neural_network'] = (nn_classifier, scaler)
            
            results["models"]["decision_tree"] = {
                "accuracy": dt_accuracy,
                "interpretable": True,
                "complexity": "Medium"
            }
            results["models"]["neural_network"] = {
                "accuracy": nn_accuracy,
                "interpretable": False,
                "complexity": "High",
                "educational_value": "Shows AI complexity vs performance trade-offs"
            }
            
            print(f"Decision Tree Accuracy: {dt_accuracy:.3f}")
            print(f"Neural Network Accuracy: {nn_accuracy:.3f}")
            print("Educational Note: Neural networks often perform better but are less interpretable")
        
        # Cross-validation for robust assessment
        if 'decision_tree' in self.models:
            cv_scores = cross_val_score(self.models['decision_tree'], X, y, cv=5)
            results["cross_validation"] = {
                "mean_accuracy": cv_scores.mean(),
                "std_accuracy": cv_scores.std(),
                "educational_note": "Cross-validation helps assess model reliability"
            }
            print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
        
        self.results[level] = results
        return results
    
    def generate_ethical_scenario(self, level: str = "ARTI1000X") -> Dict[str, str]:
        """
        Generate ethical scenarios appropriate for curriculum level.
        """
        scenarios = {
            "ARTI1000X": {
                "scenario": "A school uses an AI system to predict which students might struggle academically based on their background data (family income, previous grades, demographic information).",
                "questions": [
                    "What are the potential benefits of this system?",
                    "What biases might exist in the training data?",
                    "How could this system unfairly disadvantage certain students?",
                    "What safeguards should be in place?"
                ],
                "learning_objectives": [
                    "Understand data bias",
                    "Recognize ethical implications",
                    "Consider fairness in AI systems"
                ]
            },
            "ARTI2000X": {
                "scenario": "A healthcare AI system trained primarily on data from one demographic group is being deployed globally to diagnose diseases from medical images.",
                "questions": [
                    "How might training data limitations affect global deployment?",
                    "What are the risks of misdiagnosis across different populations?",
                    "How should regulatory frameworks address this?",
                    "What testing protocols should be mandatory before deployment?"
                ],
                "learning_objectives": [
                    "Analyze complex bias issues",
                    "Evaluate regulatory needs",
                    "Assess global AI deployment risks"
                ]
            }
        }
        return scenarios.get(level, scenarios["ARTI1000X"])
    
    def create_assessment_rubric(self, level: str) -> Dict[str, Any]:
        """
        Create assessment rubrics aligned with ARTI curriculum standards.
        """
        rubrics = {
            "ARTI1000X": {
                "theoretical_understanding": {
                    "E": "Can define basic AI concepts and identify common applications",
                    "C": "Can explain AI techniques and compare with human intelligence", 
                    "A": "Can analyze AI systems and reason about their implications"
                },
                "practical_skills": {
                    "E": "Can run and modify simple AI code with guidance",
                    "C": "Can independently implement basic AI solutions",
                    "A": "Can design and evaluate AI solutions for new problems"
                },
                "ethical_reasoning": {
                    "E": "Can identify basic ethical issues in AI",
                    "C": "Can analyze ethical implications and propose solutions",
                    "A": "Can evaluate complex ethical scenarios and regulatory needs"
                }
            },
            "ARTI2000X": {
                "advanced_applications": {
                    "E": "Understands neural networks and advanced AI applications",
                    "C": "Can implement and compare different AI approaches",
                    "A": "Can design complex AI systems and assess their risks"
                },
                "risk_assessment": {
                    "E": "Can identify risks in AI systems",
                    "C": "Can evaluate risks and propose mitigation strategies", 
                    "A": "Can conduct comprehensive risk assessments for AI deployment"
                }
            }
        }
        return rubrics.get(level, {})
    
    def generate_student_exercise(self, level: str, topic: str) -> Dict[str, Any]:
        """
        Generate contextual exercises for students.
        """
        exercises = {
            "ARTI1000X": {
                "classification": {
                    "title": "Build Your Own Classifier",
                    "description": "Modify the iris classifier to work with a different dataset",
                    "tasks": [
                        "Load a new dataset (e.g., wine quality, digits)",
                        "Train a decision tree classifier",
                        "Evaluate accuracy and discuss results",
                        "Identify potential biases in the data",
                        "Suggest improvements to the model"
                    ],
                    "code_template": self._get_exercise_template("classification_basic")
                }
            },
            "ARTI2000X": {
                "neural_networks": {
                    "title": "Compare AI Approaches",
                    "description": "Implement and compare decision tree vs neural network",
                    "tasks": [
                        "Implement both approaches on the same dataset",
                        "Compare accuracy, interpretability, and training time",
                        "Analyze when each approach is more suitable",
                        "Discuss the interpretability vs performance trade-off",
                        "Propose a hybrid approach"
                    ],
                    "code_template": self._get_exercise_template("neural_network_comparison")
                }
            }
        }
        
        return exercises.get(level, {}).get(topic, {})
    
    def _get_exercise_template(self, exercise_type: str) -> str:
        """Return code templates for exercises."""
        templates = {
            "classification_basic": '''
# Student Exercise Template: Basic Classification
from sklearn.datasets import load_wine  # Try different datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# TODO: Load your chosen dataset
data = load_wine()
X, y = data.data, data.target

# TODO: Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# TODO: Create and train your classifier
classifier = DecisionTreeClassifier(max_depth=?, random_state=42)
# Add your code here

# TODO: Evaluate and discuss your results
# Consider: What biases might exist? How could you improve the model?
            ''',
            "neural_network_comparison": '''
# Student Exercise Template: Advanced Comparison
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import time

# TODO: Implement both approaches
# TODO: Compare performance metrics
# TODO: Analyze interpretability differences
# TODO: Time the training process
# TODO: Discuss trade-offs in your report
            '''
        }
        return templates.get(exercise_type, "# Template not found")
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive report of the session.
        """
        report = f"""
# ARTI Curriculum Assessment Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Session Summary
Models evaluated: {list(self.models.keys())}
Curriculum levels covered: {list(self.results.keys())}

## Educational Insights
"""
        
        for level, results in self.results.items():
            report += f"\n### {self.curriculum_data[level]['level']}\n"
            for model_name, model_results in results["models"].items():
                report += f"- {model_name}: {model_results['accuracy']:.3f} accuracy\n"
                if 'educational_value' in model_results:
                    report += f"  Educational value: {model_results['educational_value']}\n"
        
        report += "\n## Recommendations for Teachers\n"
        report += "- Start with decision trees for interpretability\n"
        report += "- Use cross-validation to teach model reliability\n"
        report += "- Emphasize ethical considerations throughout\n"
        report += "- Progress to neural networks only after solid foundation\n"
        
        return report

def main():
    """
    Demonstration of the ARTI Curriculum Tool
    """
    print("=== ARTI Curriculum Assessment Tool ===")
    print("Building on Grok 4's foundation with enhanced functionality\n")
    
    tool = ARTICurriculumTool()
    
    # Demonstrate Level 1 (Foundation)
    level1_results = tool.demonstrate_classification("ARTI1000X")
    
    # Show ethical scenario
    ethical_scenario = tool.generate_ethical_scenario("ARTI1000X")
    print(f"\n=== Ethical Scenario (Level 1) ===")
    print(f"Scenario: {ethical_scenario['scenario']}")
    print("Discussion Questions:")
    for i, question in enumerate(ethical_scenario['questions'], 1):
        print(f"{i}. {question}")
    
    # Generate exercise
    exercise = tool.generate_student_exercise("ARTI1000X", "classification")
    print(f"\n=== Student Exercise ===")
    print(f"Title: {exercise['title']}")
    print(f"Description: {exercise['description']}")
    
    # Demonstrate Level 2 (Advanced) if requested
    level2_results = tool.demonstrate_classification("ARTI2000X")
    
    # Generate final report
    print("\n" + "="*50)
    print(tool.generate_report())
    
    return tool

# For use in educational environments
if __name__ == "__main__":
    arti_tool = main()
