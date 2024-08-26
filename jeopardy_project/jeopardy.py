#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import numpy as np

def q_word_filter(data, word_list):
    result = data
    if isinstance(word_list, str):
        word_list = [word_list]
    for word in word_list:
        alts = search_alts(word)
        result_alts = pd.DataFrame()
        for alt in alts:
            result = result[result['question_search'].str.contains(alt)]  
            result_alts = pd.concat([result_alts, result])
        result = result_alts 
    return result

def search_alts(word):
    word = word.lower()
    alt1 = " " + word
    alt2 = " " + word + ","
    alt3 = " " + word + "."
    alt4 = " " + word + "'"
    alt5 = "'" + word
    return alt1, alt2, alt3, alt4, alt5

def difficulty_filter(data, word):
    results = q_word_filter(data, word)
    mean = results.value_float.mean()
    return mean

def unique_answer_filter(data, word):
    return q_word_filter(data, word).answer.value_counts()

def get_year_data(data):
    year_data = data.groupby('year')\
                    .agg({
                        'show_id': 'nunique',
                        'value': 'count',
                        'value_float': 'mean',
                        'category': 'nunique'
                    })\
                    .apply(lambda x: round(x, 2))\
                    .rename(columns={
                        'value_float': 'mean_value', 
                        'value': 'num_questions',
                        'show_id': 'num_shows',
                        'category': 'num_categories'
                    })\
                    .reset_index()
    return year_data

def topics_by_year(data, word_list):
    result = q_word_filter(data, word_list)
    return get_year_data(result)

def getq_in_cat(data, cat):
    cat = cat.upper()
    result = data[data['category'].str.contains(cat)]\
                .groupby('category')\
                .agg({
                    'show_id': 'nunique',
                    'value': 'count',
                    'value_float': 'mean',
                    'year': ['min', 'max']
                })\
                .apply(lambda x: round(x, 2))\
                .rename(columns={
                    'value_float': 'mean_value', 
                    'value': 'num_questions',
                    'show_id': 'num_shows'
                })\
                .reset_index()
    return result

def cats_in_round(data, cat):
    result = data[data['category'].str.contains(cat.upper())]\
                .groupby(['round'])\
                .agg({'category': 'nunique', 'value': 'count', 'value_float': 'mean'})\
                .rename(columns={'category': 'num_categories', 'value':'num_questions', 'value_float': 'value_mean'})\
                .reset_index()
    return result

def display_analytics_menu(data):
    while True:
        print("\nAnalytics Menu")
        print("1. Average difficulty of questions containing a word")
        print("2. Unique answers for questions containing a word")
        print("3. Yearly breakdown of questions containing specific words")
        print("4. Questions in a specific category")
        print("5. Categories in each round")
        print("6. Return to the quiz")
        choice = input("Select an option (1-6): ")

        if choice == '1':
            word = input("Enter the word to filter by: ")
            print(f"Average difficulty of questions containing '{word}': {difficulty_filter(data, word)}")

        elif choice == '2':
            word = input("Enter the word to filter by: ")
            print(f"Unique answers for questions containing '{word}':")
            print(unique_answer_filter(data, word))

        elif choice == '3':
            words = input("Enter the words to filter by (comma separated): ").split(',')
            words = [word.strip() for word in words]
            print(f"Yearly breakdown of questions containing {', '.join(words)}:")
            print(topics_by_year(data, words))

        elif choice == '4':
            category = input("Enter the category to filter by: ")
            print(f"Questions in the '{category}' category:")
            print(getq_in_cat(data, category))

        elif choice == '5':
            category = input("Enter the category to filter by: ")
            print(f"Categories in each round for '{category}':")
            print(cats_in_round(data, category))

        elif choice == '6':
            print("Returning to the quiz...")
            break

        else:
            print("Invalid choice, please select a valid option.")

def quiz(data):
    print("Welcome to the Jeopardy Quiz Game!")
    print("You will be asked questions from a dataset of Jeopardy! questions.")
    print("Try to answer correctly, and you can set a maximum value to filter questions.")
    print("Let's start!\n")

    while True:
        value_max_resp = input('Would you like to input a maximum value? (y/n): ').strip().lower()
        if value_max_resp == 'y':
            value_max = int(input('Input a maximum value (numbers only): '))
            data = data[data['value_float'] <= value_max]
            break
        elif value_max_resp == 'n':
            break
        else:
            print("Invalid response. Please enter 'y' or 'n'.")

    exit = 0
    while exit == 0:
        qnum = np.random.randint(data.shape[0])
        row = data.iloc[qnum]
        response = input(f'In the category "{row["category"].lower()}" for {row["value"]}: {row["question"]}: ')
        
        if response.lower() == row['answer'].lower():
            print('Correct!')
        elif response.lower() in row['answer'].lower():
            print(f'Your answer is partially correct, the correct answer is: {row["answer"]}')
        else:
            print(f'Incorrect! The correct answer is: {row["answer"]}\n')
        
        next_q = input('Another question? (y/n): ').strip().lower()
        if next_q != 'y':
            exit = 1   
    print("Thank you for playing the Jeopardy Quiz Game!")
    return

if __name__ == "__main__":
    # Load and preprocess the data
    jpd = pd.read_csv('jeopardy.csv')
    jpd.rename(
        columns={
            'Show Number': 'show_id',
            ' Air Date': 'air_date',
            ' Round': 'round',
            ' Category': 'category',
            ' Value': 'value',
            ' Question': 'question',
            ' Answer': 'answer'
        }, 
        inplace=True
    )
    jpd['question_search'] = jpd.question.apply(str.lower)
    jpd['value_float'] = jpd.value.apply(lambda x: None if x == 'None' else float(x[1:].replace(',', '')))
    jpd['air_date'] = pd.to_datetime(jpd['air_date'])
    jpd['year'] = jpd['air_date'].dt.year

    # Display welcome menu
    print("Welcome to the Jeopardy Data Analysis and Quiz Game!")
    print("Choose an option from the menu below to explore the analytics or start the quiz.")

    while True:
        print("\nMain Menu")
        print("1. Analytics Menu")
        print("2. Start Quiz")
        print("3. Exit")
        main_choice = input("Select an option (1-3): ")

        if main_choice == '1':
            display_analytics_menu(jpd)

        elif main_choice == '2':
            quiz(jpd)

        elif main_choice == '3':
            print("Exiting the game. Goodbye!")
            break

        else:
            print("Invalid choice, please select a valid option.")
