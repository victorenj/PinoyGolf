## Author: Victor E Balasoto
## Last Update: 3/10/25
## Purpose: For PGT golfers use

import streamlit as st
import pandas as pd

# ----------------------------------------------------------
# > Open CLI
# > cd C:\Users\PC\Desktop\PinoyGolf
# > .venv\Scripts\activate
# > streamlit run app_strokeplay.py
# ----------------------------------------------------------


st.set_page_config(
    page_title="PGT Scorecard",
    page_icon=":golfer:",
    layout="wide",
    initial_sidebar_state="expanded"
)


def reset_scorecard():
    st.session_state.scorecard = {
        player: {f"Hole {i}": None for i in range(1, 19)} for player in ["Player 1", "Player 2", "Player 3", "Player 4"]
    }
    st.session_state.current_hole = "Hole 1"


def main():
    st.title("Pinoy Golf Tour")
    st.logo("assets/pgt_logo2_blk.jpg", size="large")

    # Initialize session state
    if "scorecard" not in st.session_state:
        reset_scorecard()
    if "current_hole" not in st.session_state:
        st.session_state.current_hole = "Hole 1"
    if "num_players" not in st.session_state:
        st.session_state.num_players = 1

    # --- Player Input Section ---
    st.sidebar.header("Player Information")
    num_players = st.sidebar.number_input("Number of Players", min_value=1, max_value=4, value=1)
    player_names = [st.sidebar.text_input(f"Enter name for Player {i + 1}", value=f"Player {i + 1}") for i in range(num_players)]
    active_players = [f"Player {i+1}" for i in range(num_players)]

    # --- Course Input Section ---
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
        st.dataframe(df)

    # --- Hole Selection ---
    holes = list(st.session_state.scorecard["Player 1"].keys())
    selected_hole = st.radio(
        "*Choose a hole :*", 
        holes, 
        horizontal=True,
        index=holes.index(st.session_state.current_hole)
    )

    # --- Score Input ---
    st.subheader(f"Enter Scores for {selected_hole}")
    scores = {}
    for idx, (playername, player) in enumerate(zip(player_names, active_players)):
        score = st.number_input(
            f"{playername}'s Score",
            min_value=1,
            max_value=10,
            value=st.session_state.scorecard[player][selected_hole] or 4,
            step=1,
            key=f"{player}_{selected_hole}_{idx}"
        )
        scores[player] = score

    # --- Score Management ---
    srcol1, srcol2 = st.columns(2)
    with srcol1:
        if st.button("Submit"):
            for player, score in scores.items():
                st.session_state.scorecard[player][selected_hole] = score
            
            current_index = holes.index(selected_hole)
            if current_index < len(holes) - 1:
                st.session_state.current_hole = holes[current_index + 1]
                st.success(f"Scores saved for {selected_hole}. Moving to {holes[current_index + 1]}!")
    
    with srcol2:
        if st.button("Reset Scores"):
            reset_scorecard()
            st.warning("All scores have been reset!")

    st.subheader("Player Scorecard")
    scorecard_data = {"Player": player_names}

    for hole in holes:
        scorecard_data[hole] = [
            st.session_state.scorecard[player][hole]
            for player in active_players
        ]

    tscol1, tscol2 = st.columns([7,1])    
    with tscol1:
        scorecard_df = pd.DataFrame(scorecard_data)
        st.dataframe(scorecard_df)

    with tscol2:        
        # Calculate total scores
        total_scores = {
            player: sum(score for score in st.session_state.scorecard[player].values() if score is not None)
            for player in active_players
        }
        for player, name in zip(active_players, player_names):
            st.write(f"**{name}:** {total_scores[player]}")

    # --- Total Scores ---
    st.subheader("🏆 Leaderboard")

    # Create sorted list of (name, score) tuples
    leaderboard = sorted(
        zip(player_names, total_scores.values()),
        key=lambda x: x[1]
    )
    
    # Display leaderboard with medals
    for rank, (name, score) in enumerate(leaderboard, start=1):
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if rank == 1:
                st.subheader("🥇")
            elif rank == 2:
                st.subheader("🥈")
            elif rank == 3:
                st.subheader("🥉")
            else:
                st.subheader(f"{rank}.")
        with col2:
            st.markdown(f"**{name}**  \n`{score} points`")
            st.progress(min(score / 72, 1))  # Assuming par 72 course

    st.download_button(
        label="Download Scorecard as CSV",
        data=scorecard_df.to_csv(index=False),
        file_name="golf_scorecard.csv",
        mime="text/csv"
    )

if __name__ == '__main__':
    main()
