"use client";

import { useState } from "react";
import { Question } from "@/lib/data/quiz";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface QuizFormProps {
  questions: Question[];
}

export function QuizForm({ questions }: QuizFormProps) {
  // State to manage the user's progress and answers
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [score, setScore] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);

  // If there are no questions, display a message.
  if (!questions || questions.length === 0) {
    return (
      <div className="flex justify-center items-center h-full">
        <p className="text-muted-foreground">No quiz questions available. Please add questions to the database.</p>
      </div>
    );
  }

  // Handle the selection of an answer option
  const handleAnswerSelect = (value: string) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questions[currentQuestionIndex].id]: value,
    }));
  };

  // Move to the next question
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  // Calculate the score and mark the quiz as completed
  const handleSubmitQuiz = () => {
    let newScore = 0;
    questions.forEach((question) => {
      if (userAnswers[question.id] === question.correct_answer) {
        newScore += 1;
      }
    });
    setScore(newScore);
    setQuizCompleted(true);
  };

  // Function to restart the quiz
  const handleRestartQuiz = () => {
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setScore(0);
    setQuizCompleted(false);
  };

  // Conditional rendering for quiz results
  if (quizCompleted) {
    return (
      <Card className="max-w-xl mx-auto">
        <CardHeader>
          <CardTitle className="text-center text-3xl font-bold">Quiz Complete!</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p className="text-xl">
            You scored <span className="font-bold">{score}</span> out of <span className="font-bold">{questions.length}</span>.
          </p>
          <p className="text-muted-foreground">
            {score === questions.length ? "Congratulations! You got a perfect score." : "Review the material and try again to improve your score!"}
          </p>
          <Button onClick={handleRestartQuiz} className="w-full">
            Restart Quiz
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Get the current question
  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const isAnswerSelected = userAnswers[currentQuestion.id] !== undefined;

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-center mb-4">
          <CardTitle>Question {currentQuestionIndex + 1} of {questions.length}</CardTitle>
          <span className="text-sm text-muted-foreground">
            {isAnswerSelected ? "Answer selected" : "Select an answer"}
          </span>
        </div>
        <p className="text-lg font-medium">{currentQuestion.text}</p>
      </CardHeader>
      <CardContent>
        <RadioGroup
          value={userAnswers[currentQuestion.id]}
          onValueChange={handleAnswerSelect}
          className="space-y-4"
        >
          {currentQuestion.options.map((option, index) => (
            <div key={index} className="flex items-center space-x-2">
              <RadioGroupItem value={option} id={`option-${index}`} />
              <Label htmlFor={`option-${index}`} className="flex-1 cursor-pointer">
                <Card className="p-4 transition-colors hover:bg-muted/50">
                  {option}
                </Card>
              </Label>
            </div>
          ))}
        </RadioGroup>
        <div className="mt-8 flex justify-end">
          {isLastQuestion ? (
            <Button onClick={handleSubmitQuiz} disabled={!isAnswerSelected}>
              Submit Quiz
            </Button>
          ) : (
            <Button onClick={handleNextQuestion} disabled={!isAnswerSelected}>
              Next Question
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
