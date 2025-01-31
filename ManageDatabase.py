import os
import logging
from dotenv import load_dotenv
from tqdm import tqdm
import libsql_experimental as sqlexp
from API_Library.FirstAPI import FirstAPI
from API_Library.APIUtils import Utils
from API_Library.API_Models.Team import Team

class TeamDataProcessor:
    def __init__(self):
        load_dotenv()

        url = os.getenv("TURSO_DATABASE_URL")
        auth_token = os.getenv("TURSO_AUTH_TOKEN")

        self.conn = sqlexp.connect("ares.db", sync_url=url, auth_token=auth_token)
        
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS season_2024 (
            teamNumber INTEGER PRIMARY KEY,
            teamName TEXT,
            sponsors TEXT,
            location TEXT,
            autoOPR REAL,
            teleOPR REAL,
            endgameOPR REAL,
            overallOPR REAL,
            autoRank INTEGER,
            teleRank INTEGER,
            endgameRank INTEGER,
            overallRank INTEGER,
            penalties INTEGER,
            penaltyRank INTEGER,
            profileUpdate INTEGER
        )
        """)
        self.conn.commit()
        
        self.season = None
    
    def load_from_database(self):
        print('Loading...')
    
    def save_to_database(self):
        """
        Save team data to the database using threading and batch processing.
        Updates rankings by merging existing data in the database with new data from the API.
        """
        first_api = FirstAPI()
        self.season = first_api.get_season(year=Utils.find_year(), debug=True, eventModes="All")

        for event in self.season.events.values():
            for team in event:
                if team.teamNumber not in self.season.rankedTeams:
                    self.season.rankedTeams[team.teamNumber] = team
                else:
                    existing_team = self.season.rankedTeams[team.teamNumber]
                    if team.overallOPR > existing_team.overallOPR:
                        existing_team.autoOPR = team.autoOPR
                        existing_team.teleOPR = team.teleOPR
                        existing_team.endgameOPR = team.endgameOPR
                        existing_team.overallOPR = team.overallOPR
                        existing_team.penalties = team.penalties
                        existing_team.profileUpdate = team.profileUpdate

        teams_list = list(self.season.rankedTeams.values())
        progress_bar = tqdm(total=len(teams_list), desc="Saving Team Data", unit=" team")
        
        team_data = [
            (
                team.teamNumber, team.teamName, team.sponsors, team.location, 
                team.autoOPR, team.teleOPR, team.endgameOPR, team.overallOPR, 
                team.autoRank, team.teleRank, team.endgameRank, team.overallRank, 
                team.penalties, team.penaltyRank, team.profileUpdate
            )
            for team in teams_list
        ]

        self.conn.executemany(
            """
            INSERT OR REPLACE INTO season_2024 (
                teamNumber, teamName, sponsors, location, autoOPR, teleOPR, endgameOPR, 
                overallOPR, autoRank, teleRank, endgameRank, overallRank, penalties, 
                penaltyRank, profileUpdate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            team_data
        )
        
        # for team in teams_list:
        #     logging.debug(f"Processing team {team.teamNumber}: {team.teamName}")
            
        #     self.conn.executemany(
        #         """
        #         INSERT OR REPLACE INTO season_2024 (
        #             teamNumber, teamName, sponsors, location, autoOPR, teleOPR, endgameOPR, 
        #             overallOPR, autoRank, teleRank, endgameRank, overallRank, penalties, 
        #             penaltyRank, profileUpdate
        #         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        #         """,
        #         (
        #             team.teamNumber, team.teamName, team.sponsors, team.location, 
        #             team.autoOPR, team.teleOPR, team.endgameOPR, team.overallOPR, 
        #             team.autoRank, team.teleRank, team.endgameRank, team.overallRank, 
        #             team.penalties, team.penaltyRank, team.profileUpdate
        #         )
        #     )

        #     progress_bar.update(1)

        self.conn.commit()
        progress_bar.close()
    
    def fetch_and_save_to_database(self):
        """
        Save team data to the database using threading and batch processing.
        Updates rankings by merging existing data in the database with new data from the API.
        """
        first_api = FirstAPI()
        self.season = first_api.get_season(year=Utils.find_year(), debug=True)

        rows = self.conn.execute(f"SELECT * FROM season_{Utils.find_year()}").fetchall()

        for row in rows:
            team_number = row[Utils.TEAM_NUMBER]
            
            if team_number not in self.season.rankedTeams:
                self.season.rankedTeams[team_number] = Team(
                    teamNumber=row[Utils.TEAM_NUMBER],
                    teamName=row[Utils.TEAM_NAME],
                    sponsors=row[Utils.SPONSORS],
                    location=row[Utils.LOCATION],
                    autoOPR=row[Utils.AUTO_OPR],
                    teleOPR=row[Utils.TELE_OPR],
                    endgameOPR=row[Utils.ENDGAME_OPR],
                    overallOPR=row[Utils.OVERALL_OPR],
                    penalties=row[Utils.PENALTIES],
                    profileUpdate=row[Utils.PROFILE_UPDATE],
                    autoRank=row[Utils.AUTO_RANK],
                    teleRank=row[Utils.TELE_RANK],
                    endgameRank=row[Utils.ENDGAME_RANK],
                    overallRank=row[Utils.OVERALL_RANK],
                    penaltyRank=row[Utils.PENALTY_RANK]
                )
            else:
                existing_team = self.season.rankedTeams[team_number]
                
                if row[Utils.OVERALL_OPR] > existing_team.overallOPR:
                    existing_team.autoOPR = row[Utils.AUTO_OPR]
                    existing_team.teleOPR = row[Utils.TELE_OPR]
                    existing_team.endgameOPR = row[Utils.ENDGAME_OPR]
                    existing_team.overallOPR = row[Utils.OVERALL_OPR]
                    existing_team.penalties = row[Utils.PENALTIES]
                    existing_team.profileUpdate = row[Utils.PROFILE_UPDATE]

        for event in self.season.events.values():
            for team in event:
                if team.teamNumber not in self.season.rankedTeams:
                    self.season.rankedTeams[team.teamNumber] = team
                else:
                    existing_team = self.season.rankedTeams[team.teamNumber]
                    if team.overallOPR > existing_team.overallOPR:
                        existing_team.autoOPR = team.autoOPR
                        existing_team.teleOPR = team.teleOPR
                        existing_team.endgameOPR = team.endgameOPR
                        existing_team.overallOPR = team.overallOPR
                        existing_team.penalties = team.penalties
                        existing_team.profileUpdate = team.profileUpdate

        self.season = Utils.generate_rankings(self.season)

        teams_list = list(self.season.rankedTeams.values())
        progress_bar = tqdm(total=len(teams_list), desc="Saving Team Data", unit=" team")
        
        team_data = [
            (
                team.teamNumber, team.teamName, team.sponsors, team.location, 
                team.autoOPR, team.teleOPR, team.endgameOPR, team.overallOPR, 
                team.autoRank, team.teleRank, team.endgameRank, team.overallRank, 
                team.penalties, team.penaltyRank, team.profileUpdate
            )
            for team in teams_list
        ]

        self.conn.executemany(
            """
            INSERT OR REPLACE INTO season_2024 (
                teamNumber, teamName, sponsors, location, autoOPR, teleOPR, endgameOPR, 
                overallOPR, autoRank, teleRank, endgameRank, overallRank, penalties, 
                penaltyRank, profileUpdate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            team_data
        )

        # for team in teams_list:
        #     logging.debug(f"Processing team {team.teamNumber}: {team.teamName}")
            
        #     self.conn.execute(
        #         """
        #         INSERT OR REPLACE INTO season_2024 (
        #             teamNumber, teamName, sponsors, location, autoOPR, teleOPR, endgameOPR, 
        #             overallOPR, autoRank, teleRank, endgameRank, overallRank, penalties, 
        #             penaltyRank, profileUpdate
        #         ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        #         """,
        #         (
        #             team.teamNumber, team.teamName, team.sponsors, team.location, 
        #             team.autoOPR, team.teleOPR, team.endgameOPR, team.overallOPR, 
        #             team.autoRank, team.teleRank, team.endgameRank, team.overallRank, 
        #             team.penalties, team.penaltyRank, team.profileUpdate
        #         )
        #     )
            # progress_bar.update(1)

        self.conn.commit()
        progress_bar.close()

def main():
    data_processor = TeamDataProcessor()
    # data_processor.fetch_and_save_to_database()
    data_processor.save_to_database()

    logging.info("Process completed successfully.")

if __name__ == "__main__":
    main()