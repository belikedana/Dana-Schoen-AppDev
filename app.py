import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import time
import random

# Code to config the page
st.set_page_config(
    page_icon="🌞")

# Use Markdown with inline CSS for custom title color
st.markdown("""
    <h1 style='color: #F39C12; font-family: "sans serif";'>
        Sunrise Ritual 🌞
    </h1>
    """, unsafe_allow_html=True)

# Filepath for stored habits, lets the user update their morning routine
HABITS_FILE = 'habits.txt'


# Definition to load the activities from the Habits File and add them to the pre-programmed activities
def load_habits():
    """Load habits from the file, including any added by the user, merging with session state."""
    if 'activities_list' not in st.session_state:
        st.session_state.activities_list = ["Drink water", "Exercise eg. Yoga", "Meditate", "Journal",
                                            "Affirmations"]  # Default habits
    if os.path.exists(HABITS_FILE):
        with open(HABITS_FILE, 'r') as file:
            file_habits = file.read().split('\n')
            for habit in file_habits:
                if habit and habit not in st.session_state.activities_list:
                    st.session_state.activities_list.append(habit)


# Definition to manipulate the Habit File, therefore to add new habits to morning routine
def add_habit(new_habit):
    """Add a new habit to the file and session state."""
    if new_habit and new_habit not in st.session_state.activities_list:
        with open(HABITS_FILE, 'a') as file:
            file.write(f"{new_habit}\n")
        st.session_state.activities_list.append(new_habit)
        st.success(f"Added habit: {new_habit}")


# Handling the Dataset for the morning routine
def append_morning_routine_to_csv(routine_date, activities):
    """Append or update morning routine data in the CSV file."""
    file_path = 'morning_routine.csv'
    formatted_date = routine_date.strftime('%Y-%m-%d')

    # Define the DataFrame columns dynamically based on the activities dictionary keys
    columns = ['Date'] + list(activities.keys())

    # Try to read the existing CSV file into a DataFrame; if it doesn't exist, create an empty DataFrame with defined columns
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=columns)

    # Check if there's an entry for the specified date
    if formatted_date in df['Date'].values:
        # If the date exists, update the row for this date
        df.loc[df['Date'] == formatted_date, list(activities.keys())] = list(activities.values())
    else:
        # If there's no entry for the specified date, create a new one
        new_row = pd.DataFrame([[formatted_date] + list(activities.values())], columns=columns)
        df = pd.concat([df, new_row], ignore_index=True)

    # Ensure all activity columns are integers
    for activity in activities.keys():
        if activity in df.columns:
            df[activity] = df[activity].fillna(0).astype(int)
        else:
            df[activity] = 0  # Add the column with default 0 if it doesn't exist

    # Write the DataFrame back to the CSV, overwriting the existing file
    df.to_csv(file_path, index=False)


# Handling the Dataset for the nightly survey
def append_nightly_survey_to_csv(routine_date, energy_level, mood, productivity, routine_satisfaction, water_intake,
                                 phone_usage, exercise, breakfast, meditation_mindfulness, additional_comments):
    """
    Append nightly survey data to the nightly survey CSV file.
    """
    file_path = 'nightly_survey.csv'

    # Format the date
    formatted_date = routine_date.strftime('%Y-%m-%d')
    survey_data = {
        'Date': formatted_date,
        'Energy Level': energy_level,
        'Mood': mood,
        'Productivity': productivity,
        'Routine Satisfaction': routine_satisfaction,
        'Water Intake': water_intake,
        'Phone Usage': phone_usage,
        'Exercise': exercise,
        'Breakfast': breakfast,
        'Meditation/Mindfulness': meditation_mindfulness,
        'Additional Comments': additional_comments
    }

    # Load the existing data or create a new DataFrame if the file doesn't exist
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=survey_data.keys())

    # Check if there's an existing entry for the given date
    mask = df['Date'] == formatted_date
    if mask.any():
        # Update existing entry
        for key, value in survey_data.items():
            df.loc[mask, key] = value
    else:
        # Append a new entry
        new_entry_df = pd.DataFrame([survey_data])
        df = pd.concat([df, new_entry_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV, overwriting the old file
    df.to_csv(file_path, index=False)


# App Pages: First Page that lets the User track their morning
def track_morning():
    st.header("Track Your Morning Routine")
    with st.expander("What is the Morning Routine Tracker for?"):
        st.write(
            "The habit tracker shows you the progress you made with your morning routine, if you fully committed to it "
            "or if there is room for improvement. More easily put it is a overview of your habits in the morning.")

    date_input = st.date_input("Date", value=date.today())

    # Initialize a dictionary to hold the status of each activity
    activities_status = {activity: False for activity in st.session_state.activities_list}

    with st.form("routine_tracking_form"):
        # Dynamically create checkboxes for each activity in the session state
        for activity in st.session_state.activities_list:
            activities_status[activity] = st.checkbox(activity, key=activity)

        submitted = st.form_submit_button("Submit")

        if submitted:
            # Prepare the data for CSV append
            activities_data = {activity: 1 if status else 0 for activity, status in activities_status.items()}
            append_morning_routine_to_csv(date_input, activities_data)
            st.success("Morning routine tracked!")

    # Adding new habit functionality outside the form to avoid confusion
    new_habit = st.text_input("Add a new morning habit:")
    if st.button("Add Habit"):
        add_habit(new_habit)


# App Pages: Lets the User view the morning routine data
def view_morning_routine_data():
    """Display the user's morning routine data."""
    try:
        df = pd.read_csv('morning_routine.csv')
        st.write(df)
    except FileNotFoundError:
        st.write("No morning routine data available.")


# App Pages: Nightly Survey Application
def display_nightly_survey():
    """
    The nightly survey used to analyze the affect of the morning routine on the rest of their day.
    """
    st.header("Nightly Survey")
    with st.expander("What is the Nightly Survey for?"):
        st.write("The nightly survey needs to be filled out every night and is a chance for you to reflect on your day "
                 "and how your morning routine has prepared you for it. It is essential for the analysis of the effectiveness of the morning routine.")

    with st.form("nightly_survey_form", clear_on_submit=True):
        date_input = st.date_input("Date", value=datetime.now())
        energy_level = st.slider("How would you rate your energy level throughout the day?", 1, 5, 3)
        mood = st.selectbox("Overall, how was your mood today?", ["Great", "Good", "Neutral", "Bad", "Terrible"])
        productivity = st.slider("How productive did you feel today?", 1, 5, 3)
        routine_satisfaction = st.slider("How satisfied were you with your morning routine today?", 1, 5, 3)
        water_intake = st.radio("Did you drink water first thing in the morning?", ("Yes", "No"))
        phone_usage = st.radio("Did you use your phone within the first hour of waking up?", ("Yes", "No"))
        exercise = st.radio("Did you engage in any form of exercise in the morning?", ("Yes", "No"))
        breakfast = st.radio("Did you have breakfast within the first hour of waking up?", ("Yes", "No"))
        meditation_mindfulness = st.radio("Did you practice meditation or mindfulness in the morning?", ("Yes", "No"))
        additional_comments = st.text_area("Any additional comments on how your morning routine affected your day?")

        submit_button = st.form_submit_button("Submit Survey")

        if submit_button:
            append_nightly_survey_to_csv(
                routine_date=date_input,
                energy_level=energy_level,
                mood=mood,
                productivity=productivity,
                routine_satisfaction=routine_satisfaction,
                water_intake=water_intake,
                phone_usage=phone_usage,
                exercise=exercise,
                breakfast=breakfast,
                meditation_mindfulness=meditation_mindfulness,
                additional_comments=additional_comments
            )
            st.success("Survey submitted successfully!")


# Data Analysis part
# In order to be able to analyze the data, we need to have only numerical data
def convert_responses_to_numeric(df):
    """
    We need to convert string data into numerical data for the correlation matrix.
    """
    # Mapping for ordinal responses like mood
    mood_mapping = {
        "Terrible": 1,
        "Bad": 2,
        "Neutral": 3,
        "Good": 4,
        "Great": 5
    }
    # Apply the mapping to the Mood column if it exists
    if 'Mood' in df.columns:
        df['Mood'] = df['Mood'].map(mood_mapping)

    # Mapping for binary responses (Yes/No)
    binary_mapping = {
        "Yes": 1,
        "No": 0}
    # List of columns with binary responses to convert
    binary_response_columns = ['Water Intake', 'Phone Usage', 'Exercise', 'Breakfast', 'Meditation/Mindfulness']
    for column in binary_response_columns:
        if column in df.columns:
            df[column] = df[column].map(binary_mapping)

    return df


# Load and prepare the data for the analysis
def load_data():
    """
        Load and merge morning routine and nightly survey data, converting string responses to numeric.
        Returns the merged DataFrame and the analysis period.
        """
    # Load morning routine data
    morning_df = pd.read_csv('morning_routine.csv')
    # Load nightly survey data
    nightly_df = pd.read_csv('nightly_survey.csv')

    # Convert string responses to numeric
    nightly_df = convert_responses_to_numeric(nightly_df)

    # Merge the two datasets on the Date column
    merged_df = pd.merge(morning_df, nightly_df, on='Date', how='inner')
    analysis_period = f"{merged_df['Date'].min()} to {merged_df['Date'].max()}"
    return merged_df, analysis_period


# Analyze the Data for Insights
def analyze_data(merged_df):
    # Select only numeric columns for correlation analysis
    numeric_df = merged_df.select_dtypes(include=['number'])
    # Compute the correlation matrix
    correlation_matrix = numeric_df.corr()
    return correlation_matrix


def load_and_analyze_data():
    """
    Load data from files, prepare it, and perform correlation analysis.
    Returns the correlation matrix along with the merged DataFrame and analysis period.
    """
    merged_df, analysis_period = load_data()  # Load and prepare data
    if merged_df is not None:
        correlation_matrix = analyze_data(merged_df)  # Perform correlation analysis
        return correlation_matrix, merged_df, analysis_period
    else:
        return None, None, None


# Definition to display the consistency the user has in their morning routine
def view_morning_routine_consistency():
    """
    Calculates and displays the consistency of completing each habit in the morning routine
    based on the current list of habits in the session state.
    """
    try:
        # Load the morning routine data from a CSV file.
        df = pd.read_csv('morning_routine.csv')
        # Convert the 'Date' column to datetime format for easier manipulation.
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        # Check if the DataFrame is not empty and the session state has a list of habits.
        if not df.empty and 'activities_list' in st.session_state:
            # Count the unique dates to know over how many days tracking has occurred.
            total_days_tracked = df['Date'].nunique()
            # Retrieve the list of habits from the session state.
            habits = st.session_state.activities_list

            # Initialize a dictionary to store consistency percentages for each habit.
            habit_consistency = {}
            for habit in habits:
                # Check if the habit has been tracked (exists as a column in the DataFrame).
                if habit in df.columns:
                    # Calculate the mean of each habit column and multiply by 100 for percentage.
                    habit_consistency[habit] = (df[habit].mean() * 100)
                else:
                    # If a habit hasn't been tracked, its consistency is 0%.
                    habit_consistency[habit] = 0.0

            # Display the analysis header and the total number of days tracked.
            st.subheader("Morning Routine Consistency Analysis")
            st.write(f"Tracked over: {total_days_tracked} days")

            # Calculate and display the overall consistency percentage.
            overall_consistency = sum(habit_consistency.values()) / len(habits) if habits else 0
            st.metric("Overall Consistency", f"{overall_consistency:.2f}%")

            # Display the consistency percentage for each habit.
            for habit, consistency in habit_consistency.items():
                st.metric(f"{habit} Consistency", f"{consistency:.2f}%")

            # Provide feedback to the user based on the overall consistency.
            if overall_consistency < 60:
                st.warning(
                    "Your morning routine consistency is below 60%. Consider being more consistent or adjusting your routine.")
            else:
                st.success("Great job! You're maintaining a good consistency in your morning routine.")
        else:
            # Show an error message if no data is found.
            st.error("No data found. Start tracking your morning routine to view consistency analysis.")

    except FileNotFoundError:
        # Show an error message if the CSV file does not exist.
        st.error("Morning routine data file not found. Please ensure you've tracked your habits.")


# Provide Insights
# Recommendations and Insight Definitions Part
def recommendation():
    """
    Recommendations on Phone Usage, Affirmations, Exercise and Meditation and how these activities impact the user.
    """
    correlation_matrix, merged_df, analysis_period = load_and_analyze_data()

    # Begin displaying the Recommendations section in the app interface
    st.write("## Recommendations:")

    # Check if both 'Phone Usage' and 'Productivity' are present as columns in the correlation matrix
    # This is to ensure that the analysis only proceeds if relevant data is available
    if 'Phone Usage' in correlation_matrix.columns and 'Productivity' in correlation_matrix.columns:
        # Calculate the correlation coefficient between phone usage in the morning and productivity levels
        phone_usage_productivity_corr = correlation_matrix.loc['Phone Usage', 'Productivity']
        # If the correlation is negative, it indicates that increased phone usage is associated with lower productivity
        if phone_usage_productivity_corr < 0:
            # Present a specific recommendation to the user based on this finding
            st.subheader("Limit Morning Phone Use")
            st.write("""
                    - **Recommendation**: Limit your phone usage during the first hour after waking up.
                    - **Why**: Analysis has revealed a negative correlation between morning phone usage and productivity. 
                               This suggests that reducing early screen time may help enhance your focus on daily goals 
                               and lead to a more productive day. By limiting phone usage, you can avoid distractions and 
                               potentially improve your overall productivity.
                    """)

    if 'Affirmations' in correlation_matrix.columns and 'Routine Satisfaction' in correlation_matrix.columns:
        affirmations_satisfaction_corr = correlation_matrix.loc['Affirmations', 'Routine Satisfaction']
        if affirmations_satisfaction_corr > 0:
            st.subheader("Incorporate Affirmations")
            st.write("""
                    - **Recommendation**: Make affirmations a regular part of your morning routine.
                    - **Why**: Practicing affirmations in the morning is positively correlated with routine satisfaction. Affirmations can help set a positive tone for the day, boosting confidence and aligning your mindset with your goals.
                    """)

    if 'Affirmations' in correlation_matrix.columns and 'Mood' in correlation_matrix.columns:
        affirmations_mood_corr = correlation_matrix.loc['Affirmations', 'Mood']
        if affirmations_mood_corr > 0:
            st.subheader("Affirmations for a Better Mood")
            st.write("""
                    - **Recommendation**: Start your day with positive affirmations.
                    - **Why**: There's a positive correlation between morning affirmations and mood. This simple practice can help improve your outlook, reduce stress, and enhance emotional well-being.
                    """)

    if 'Exercise eg. Yoga' in correlation_matrix.columns and 'Energy Level' in correlation_matrix.columns:
        exercise_energy_corr = correlation_matrix.loc['Exercise eg. Yoga', 'Energy Level']
        if exercise_energy_corr > 0:
            st.subheader("Morning Exercise Boosts Energy")
            st.write("""
                    - **Recommendation**: Include physical activity, like yoga, in your morning routine.
                    - **Why**: Engaging in exercise in the morning is associated with higher energy levels. Physical activity can increase endorphin levels, improving mood and vitality throughout the day.
                    """)

    if 'Meditate' in correlation_matrix.columns and 'Productivity' in correlation_matrix.columns:
        meditation_productivity_corr = correlation_matrix.loc['Meditate', 'Productivity']
        if meditation_productivity_corr > 0:
            st.subheader("Meditation for Productivity")
            st.write("""
                    - **Recommendation**: Practice meditation or mindfulness in the morning.
                    - **Why**: Morning meditation is linked to higher productivity. It can help clear your mind, reduce stress, and enhance focus, allowing for more effective task management and decision-making.
                    """)


# Definition analyzes how morning routine activities correlate to outcomes like mood and productivity
def get_activity_outcome_correlations(correlation_matrix, activities, outcomes):
    """Extract correlations between specified activities and outcomes. Needed for the personalized insight"""
    correlations = {}
    for activity in activities:
        for outcome in outcomes:
            # Check if both activity and outcome exist in the correlation matrix
            if activity in correlation_matrix.index and outcome in correlation_matrix.columns:
                # Extract the correlation coefficient between the activity and outcome
                corr_value = correlation_matrix.at[activity, outcome]

                # Only consider correlations that are significant (absolute value greater than 0.2)
                if pd.notnull(corr_value) and abs(corr_value) > 0.2:
                    correlations[(activity, outcome)] = corr_value
    return correlations


# Definition categorizes the correlation into positive and negative impacts
def generate_categorized_recommendations(correlations):
    """Generate categorized recommendations based on the direction of correlations. Needed for the personalized insight"""
    # Separate activities into those with positive and negative impacts based on correlation values
    positive_impacts = {pair: corr for pair, corr in correlations.items() if corr > 0}
    negative_impacts = {pair: corr for pair, corr in correlations.items() if corr < 0}

    # Display activities with positive impacts and recommend continuing or increasing them
    if positive_impacts:
        st.write("### This Works for You")
        for (activity, outcome), corr_value in positive_impacts.items():
            st.write(f"- **{activity}** positively impacts your **{outcome}**. "
                     "Keeping it up could further enhance your well-being.")

    # Display activities with negative impacts and suggest reconsideration or reduction
    if negative_impacts:
        st.write("### Improve This")
        for (activity, outcome), corr_value in negative_impacts.items():
            st.write(f"- **{activity}** might be hindering your **{outcome}**. "
                     "Consider adjusting or reducing this activity to see improvements.")


# Definition to shows the personalized insights
def show_personalized_insights():
    """Display personalized insights and recommendations based on the user's morning routine data."""
    # Load the user data and perform analysis to get the correlation matrix and the period of analysis.
    # This includes combining morning routine data with outcomes from the nightly survey.
    correlation_matrix, merged_df, analysis_period = load_and_analyze_data()

    # Inform the user about the period over which the analysis is conducted.
    st.write(f"Analysis based on data from: {analysis_period}")

    # A friendly greeting message to introduce the insights section.
    greeting = f"Good morning! Here's how to optimize your morning routine:"
    st.write(greeting)

    # Specifying which columns in the data are considered activities and which are considered outcomes.
    # This helps focus the analysis on relevant aspects of the morning routine.
    activities = ['Drink Water', 'Exercise eg. Yoga', 'Meditate', 'Journal', 'Affirmations']
    outcomes = ['Energy Level', 'Mood', 'Routine Satisfaction']

    # Calculate the correlations between specified activities and outcomes.
    # This helps identify which activities have the most significant positive or negative impact on outcomes.
    correlations = get_activity_outcome_correlations(correlation_matrix, activities, outcomes)

    # Present the calculated correlations in a categorized manner, highlighting activities
    # that positively or negatively impact the user's well-being.
    generate_categorized_recommendations(correlations)


# Definition to display the really detailed insights
def detailed_insights():
    """
    Provides very detailed insights because it shows the correlation numbers of the activities with the outcomes.
    """
    correlation_matrix, merged_df, analysis_period = load_and_analyze_data()

    # Present broader insights based on the full correlation matrix
    activities = ['Drink Water', 'Exercise eg. Yoga', 'Meditate', 'Journal', 'Affirmations', 'Phone Usage']
    outcomes = ['Energy Level', 'Mood', 'Productivity', 'Routine Satisfaction']

    st.write("### Key Insights")

    for activity in activities:
        # Check if the activity is in the correlation matrix to ensure relevance.
        if activity in correlation_matrix.index:
            for outcome in outcomes:
                # Ensure the outcome is also in the correlation matrix before analyzing.
                if outcome in correlation_matrix.columns:
                    corr_value = correlation_matrix.at[activity, outcome]
                    # Proceed only if the correlation value is valid (not null).
                    if pd.notnull(corr_value):
                        # Positive correlation suggests a beneficial impact of the activity.
                        if corr_value > 0.2:
                            st.write(f"- **{activity}** positively correlates with **{outcome}** ({corr_value:.2f}).")
                        # Negative correlation suggests the activity might be adversely affecting the outcome.
                        elif corr_value < -0.2:
                            st.write(f"- **{activity}** negatively correlates with **{outcome}** ({corr_value:.2f}).")


# Community Page
def display_user_box(name, completion_percentage, action_button_label):
    """Display user progress and action button."""
    with st.container():
        st.subheader(f"{name}'s Monthly Progress")
        st.write(f"Completion Percentage: {completion_percentage}%")
        if st.button(action_button_label, key=f"button_{name}"):
            st.success(f"{action_button_label} sent to {name}!")


def community_page():
    st.header("Community Page")

    with st.expander("What is the Community Page for?"):
        st.write(
            "Here you can add your friends to embark on this miraculous journey to improve your life. After adding them"
            " to your friend list, you can see their monthly progress on the morning routine they committed to. To motivate "
            "them, you can send motivation or success if they are doing a good job sticking to their commitment. Share this "
            "app with your friends to also gain their support and admiration."
        )

    # Example users
    col1, col2 = st.columns(2)
    with col1:
        display_user_box("Annette", 80, "Send Congrats")
    with col2:
        display_user_box("Lisa", 30, "Send Motivation")

    # Friend name input
    friend_name = st.text_input("Enter your friend's name:")
    if st.button("Send Friend Request", key="send_request"):
        # If a name entered then success, if not warning
        if friend_name:
            st.success(f"Friend request sent to {friend_name}!")
        else:
            st.warning("Please enter your friend's name before sending the request.")


# Reminders Page
def reminders_page():
    st.header("Reminders")

    # As an Easter Egg, some surprise compliments
    compliments = [
        "You're doing great!",
        "Keep up the amazing work!",
        "You're a superstar!",
        "Remember, you're awesome!",
        "Today is going to be a good day!"]

    with st.expander("What are the Reminders for?"):
        st.write(
            "Set reminders that will alert you when it is time to start your morning routine and when to fill out your "
            "nightly survey. This ensures you stay committed to your morning routine and to the survey, "
            "which is needed to complete the analysis and suggest personalized recommendations."
        )

    # Submit the reminders, that displays the compliment as well
    with st.form("reminder_form"):
        st.time_input("Morning Routine Reminder", key="morning")
        st.time_input("Survey Reminder", key="survey")
        submitted = st.form_submit_button("Set Reminders")
        if submitted:
            st.success("Reminders set successfully!")
            st.success(random.choice(compliments) + " 🌟")


# Challenges as an Easter egg for the user displayed on the first page
challenges = [
    "Write down three things you're grateful for today.",
    "Take a five-minute stretch break.",
    "Drink a glass of water right now.",
    "Send a kind message to a friend or family member.",
    "Take three deep breaths and focus on your breathing."
]


# The Main Definition that creates the app pages
def main():
    # Image with the Image address from GitHub
    st.image('https://github.com/belikedana/Dana-Schoen-AppDev/blob/main/images/sunrise3.jpeg?raw=true',
             caption='Have a wonderful day!')
    load_habits()

    # Navigation
    app_mode = st.sidebar.selectbox("MENU",
                                    ["Track Morning Routine", "Complete Nightly Survey", "View Insights",
                                     "Community Page", "Reminders"])

    # App Mode of the Tracking Page
    if app_mode == "Track Morning Routine":
        track_morning()
        if st.button("View Consistency"):
            view_morning_routine_consistency()
            view_morning_routine_data()
        st.write("-------------------------------------")
        # Easter Egg with the Challenge
        if st.button('Show me today\'s challenge!'):
            st.markdown(f"**Today's Challenge:** {random.choice(challenges)}")

    # App Mode of the Nightly Survey
    elif app_mode == "Complete Nightly Survey":
        display_nightly_survey()

    # App Mode of the Insights
    elif app_mode == "View Insights":
        st.header("Your Morning Routine Insights")

        col1, col2 = st.columns([1, 1])  # Adjust the ratio as needed
        with col1:
            with st.expander("What is the Analysis for?"):
                st.write(
                    "The analysis give you insights in how your morning routine affects your day. It gives you recommendations"
                    " on what to improve, which habits are essential for you and which stop you from reaching your ultimate potential. ")
        with col2:
            with st.expander("How does an optimal morning routine look like?"):
                st.write(
                    "The optimal morning routine includes: Silence (Meditation), Affirmations (spoken or written down), Visualization (eg. your goals), Exercise (Exercise the body), Reading (5 mins of reading), Journal")
        option = st.selectbox(
            "Choose Your Analysis:",
            ["Overview Analysis", "A More Detailed Analysis"]
        )

        # Added a little timer, so it appears like the app needs to retrieve the data first before displaying it
        if option == "Overview Analysis":
            # Create a placeholder for a loading message
            loading_message = st.empty()
            # Display a loading message
            loading_message.text("Loading data... Please wait.")
            # Simulate data loading
            time.sleep(2)  # Pause for 2 seconds to simulate data processing
            # Now that the data is (supposedly) loaded, clear the loading message
            loading_message.empty()
            # Continue with the rest of your app
            with st.expander("Your Analysis:"):
                # Display a button for the user to analyze their routine
                show_personalized_insights()
                recommendation()
                st.warning(
                    "**Disclaimer:** The analysis provided by this tool is based on patterns detected by an algorithm, which might reveal insights not immediately apparent. However, it's crucial to stay in tune with your own body and how your morning routine affects your well-being. Trust your judgment and feelings in deciding what's best for you, irrespective of the recommendations.")
        # More Detailed Analysis that loads the detailed_insights
        elif option == "A More Detailed Analysis":
            # Create a placeholder for a loading message
            loading_message = st.empty()
            # Display a loading message
            loading_message.text("Loading data... Please wait.")
            # Simulate data loading
            time.sleep(2)  # Pause for 2 seconds to simulate data processing
            # Now that the data is (supposedly) loaded, clear the loading message
            loading_message.empty()
            with st.expander("Detailed Analysis:"):
                detailed_insights()

    # App Mode of the Community Page
    elif app_mode == "Community Page":
        community_page()

    # App Mode of the Reminders
    elif app_mode == "Reminders":
        reminders_page()


# Call the Main Definition to display the app
main()
