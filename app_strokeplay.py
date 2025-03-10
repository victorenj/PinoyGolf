## Author: Victor E Balasoto
## Last Update: 2/24/25
## Purpose: For PGT golfers use

# ----------------------------------------------------------
# > Open CLI
# > cd C:\Users\PC\Desktop\Golf
# > .venv\Scripts\Activate.bat
# > streamlit run app_strokeplay.py
# ----------------------------------------------------------


import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="PGT Scorecard",
    page_icon=":golfer:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to reset the scorecard
def reset_scorecard():
    st.session_state.scorecard = {
        player: {f"Hole {i}": None for i in range(1, 19)} for player in ["Player 1", "Player 2", "Player 3", "Player 4"]
    }
    st.session_state.current_hole = "Hole 1"


def main():
    st.title("Pinoy Golf Tour")

    # Initialize session state for scorecard and current hole
    if "scorecard" not in st.session_state:
        st.session_state.scorecard = {
            player: {f"Hole {i}": None for i in range(1, 19)} for player in ["Player 1", "Player 2", "Player 3", "Player 4"]
        }
    if "current_hole" not in st.session_state:
        st.session_state.current_hole = "Hole 1"
    if "num_players" not in st.session_state:
        st.session_state.num_players = 1

    # --- Sidebar for course input ---
    st.logo("assets/pgt_logo2_blk.jpg", size="large")
    st.sidebar.header("Golf Course Information")

    course_name = ["Knights Play", "Brevofield", "Quaker Creek", "Raleigh GA", "Zebulon CC", "Custom"]
    selected_course = st.sidebar.selectbox("Golf Course", course_name)

    if selected_course == "Custom":
        custom_input = st.sidebar.text_input("Write the name of Golf Course :")
        if custom_input:
            st.subheader(f'**_{custom_input} Golf Course_**')
    else:
        st.subheader(f'**_{selected_course} Golf Course_**')

    try:
        df_all = pd.read_excel('assets/GolfCoursePar.xlsx')
        course_mapping = {
        'Knights Play': [0, 1],
        'Brevofield': [0, 2],
        'Quaker Creek': [0, 3],
        'Raleigh GA': [0, 4],
        'Zebulon CC': [0, 5]
        }

        if selected_course in course_mapping:
            cols = course_mapping[selected_course]
            df = df_all.iloc[:, cols].T  # Transpose the DataFrame for display
            df.iloc[1:, :] = df.iloc[1:, :].fillna(0).astype(int)
        else:
            pass
            df = pd.DataFrame()  # Empty DataFrame if no match
        
    except Exception as e:
        st.error(f"An error occurred while loading the file: {e}")

    if selected_course != "Custom":
        st.write("*Scorecard*")
        st.dataframe(df)

    # --- Sidebar for player input ---
    st.sidebar.header("Player Information")
    num_players = st.sidebar.number_input("Number of Players", min_value=1, max_value=4, value=1)
    player_names = []
    
    for i in range(num_players):
        player_name = st.sidebar.text_input(f"Enter name for Player {i + 1}", value=f"Player {i + 1}")
        player_names.append(player_name)

    # Get the list of active players based on the selected number
    active_players = [f"Player {i}" for i in range(1, num_players + 1)]

    # Radio buttons for selecting the current hole
    st.subheader("Select a Hole")
    holes = list(st.session_state.scorecard["Player 1"].keys())
    selected_hole = st.radio(
        "Choose a hole:", 
        holes, 
        horizontal=True,
        index=holes.index(st.session_state.current_hole)
    )
    
    # Number inputs for entering scores for each player
    st.subheader(f"Enter Scores for {selected_hole}")
    scores = {}
    for playername, player in zip(player_names, active_players):
        score = st.number_input(
            f"{playername}'s Score",
            min_value=1,  # Minimum possible score
            max_value=10,  # Maximum possible score (adjust as needed)
            value=st.session_state.scorecard[player][selected_hole] or 4,  # Default value or previously entered score
            step=1,
            key=f"{player}_{selected_hole}"  # Unique key per player and hole
        )
        scores[player] = score

    srcol1, srcol2 = st.columns(2)
    with srcol1:
        # Submit button to save the scores and move to the next hole
        if st.button("Submit"):
            # Save the entered scores to the scorecard
            for player, score in scores.items():
                st.session_state.scorecard[player][selected_hole] = score
        
            # Move to the next hole if available
            current_index = holes.index(selected_hole)
            if current_index < len(holes) - 1:
                st.session_state.current_hole = holes[current_index + 1]
                st.success(f"Scores saved for {selected_hole}. Moving to {holes[current_index + 1]}!")
            else:
                st.success(f"Scores saved for {selected_hole}. You have completed all holes!")
    
    with srcol2:
        # Reset button to reset all scores
        if st.button("Reset Scores"):
            reset_scorecard()
            st.warning("All scores have been reset!")
    
    # Restructure the scorecard data to show players in rows and holes as columns
    st.subheader("Player Scorecard")
    scorecard_data = {
        "Player": player_names,
    }
    for hole in holes:
        scorecard_data[hole] = [st.session_state.scorecard[player][hole] for player_name in player_names]
    
    scorecard_df = pd.DataFrame(scorecard_data)
    
    # Display the scorecard DataFrame
    st.dataframe(scorecard_df)

    # Optional: Add a download button to save the scorecard as a CSV file
    csv = scorecard_df.to_csv(index=False)

    tcol1, tcol2 = st.columns(2)
    with tcol1:
        # Calculate total scores for each player
        total_scores = {
            player: sum(score for score in st.session_state.scorecard[player].values() if score is not None)
            for player in active_players
        }
        
        # Display total scores after the scorecard
        st.subheader("Total Scores")
        for player_name, total_score in zip(player_names, total_scores.items()):
            st.write(f"**{player_name}:** {total_score}")
    
    with tcol2:
        st.download_button(
            label="Download Scorecard as CSV",
            data=csv,
            file_name="golf_scorecard.csv",
            mime="text/csv"
        )

if __name__ == '__main__':
    main()