from API_Library.API_Models.Team import Team
from datetime import datetime

class Utils:
    TEAM_NUMBER = 0
    TEAM_NAME = 1
    SPONSORS = 2
    LOCATION = 3
    AUTO_OPR = 4
    TELE_OPR = 5
    ENDGAME_OPR = 6
    OVERALL_OPR = 7
    AUTO_RANK = 8
    TELE_RANK = 9
    ENDGAME_RANK = 10
    OVERALL_RANK = 11
    PENALTIES = 12
    PENALTY_RANK = 13
    PROFILE_UPDATE = 14

    @staticmethod
    def generate_rankings(season):
        """
        Rank the teams across all events in the season based on various OPR categories.

        Arguments:
            season (Season): The Season object containing all events and teams.

        Modifies:
            The rankedTeams in the season object by adding rank attributes (autoRank, teleRank, endgameRank, overallRank, penaltyRank)
        """
        for event in season.events.values():
            if len(event) > 0:
                for team in event: 
                    Utils._process_team_data(season, team)

        Utils._generate_individual_rankings(season.rankedTeams)

        return season

    @staticmethod
    def _process_team_data(season, team_data):
        """
        Process the team data and update the dictionary.

        Arguments:
            season (Season): The Season object where the team data should be added/updated.
            team_data (Team): The Team object containing the new team data.
        """
        team_number = team_data.teamNumber
        team_name = team_data.teamName
        sponsors = team_data.sponsors
        location = team_data.location
        auto_opr = team_data.autoOPR
        tele_opr = team_data.teleOPR
        endgame_opr = team_data.endgameOPR
        overall_opr = team_data.overallOPR
        penalties = team_data.penalties
        modified_on = team_data.profileUpdate

        if team_number not in season.rankedTeams:
            season.rankedTeams[team_number] = Team(
                teamNumber=team_number,
                teamName=team_name,
                sponsors=sponsors,
                location=location,
                autoOPR=auto_opr,
                teleOPR=tele_opr,
                endgameOPR=endgame_opr,
                overallOPR=overall_opr,
                penalties=penalties,
                profileUpdate=modified_on,
            )
        else:
            existing_team = season.rankedTeams[team_number]
            Utils._update_team_data(existing_team, team_data)

    @staticmethod
    def _update_team_data(existing_team, team_data):
        """
        Update the team data if the new data is better or more recent.

        Arguments:
            existing_team (Team): The existing team in the rankedTeams dictionary.
            team_data (Team): The new team data to compare and possibly update.
        """
        if team_data.overallOPR > existing_team.overallOPR:
            existing_team.autoOPR = team_data.autoOPR
            existing_team.teleOPR = team_data.teleOPR
            existing_team.endgameOPR = team_data.endgameOPR
            existing_team.overallOPR = team_data.overallOPR
            existing_team.penalties = team_data.penalties
        
        if team_data.profileUpdate > existing_team.profileUpdate:
            existing_team.profileUpdate = team_data.profileUpdate

    @staticmethod
    def _generate_individual_rankings(team_data):
        """
        Generate individual rankings for the teams based on OPR categories.

        Arguments:
            team_data (dict): A dictionary where the key is the team number and the value is the Team object.
        """
        auto_ranking = sorted(team_data.values(), key=lambda t: t.autoOPR, reverse=True)
        tele_ranking = sorted(team_data.values(), key=lambda t: t.teleOPR, reverse=True)
        endgame_ranking = sorted(team_data.values(), key=lambda t: t.endgameOPR, reverse=True)
        overall_ranking = sorted(team_data.values(), key=lambda t: t.overallOPR, reverse=True)
        penalties_ranking = sorted(team_data.values(), key=lambda t: t.penalties)

        Utils._assign_ranks(auto_ranking, 'autoRank')
        Utils._assign_ranks(tele_ranking, 'teleRank')
        Utils._assign_ranks(endgame_ranking, 'endgameRank')
        Utils._assign_ranks(overall_ranking, 'overallRank')
        Utils._assign_ranks(penalties_ranking, 'penaltyRank')

    @staticmethod
    def _assign_ranks(ranking, rank_type):
        """
        Assign ranks to the teams based on the given ranking list.

        Arguments:
            ranking (list): The list of teams sorted by a specific OPR value.
            rank_type (str): The name of the rank attribute to assign (e.g., 'autoRank').
        """
        for idx, team in enumerate(ranking, start=1):
            setattr(team, rank_type, idx)
    
    @staticmethod
    def find_year():
        current_date = datetime.now()
        return current_date.year - 1 if current_date.month < 8 else current_date.year