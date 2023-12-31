def get_mapped_stat(stat_type):
    stat_mapping = {
        "Pass Completions": "PassingCompletions",
        "Pass Yards": "PassingYards",
        "Pass TDs": "PassingTouchdowns",
        "Pass Attempts": "PassingAttempts",
        "Fumbles Lost": "FumblesLost",
        "INT": "Interceptions",
        "Pass INTs": "Interceptions",
        "Receptions": "Receptions",
        "Receiving Yards": "ReceivingYards",
        "Rec TDs": "ReceivingTouchdowns",
        "Rec Targets": "ReceivingTargets",
        "Rush Yards": "RushingYards",
        "Rush Attempts": "RushingAttempts",
        "Rush TDs": "RushingTouchdowns",
        "Fantasy Score": "FantasyScore",
        "Touchdowns": "Touchdowns",
        "Pass+Rush+Rec TDs": "PassingTouchdowns,RushingTouchdowns,ReceivingTouchdowns",
        "Rush+Rec TDs": "RushingTouchdowns,ReceivingTouchdowns",
        "Pass+Rush Yds": "PassingYards,RushingYards",
        "Rec+Rush Yds": "RushingYards,ReceivingYards",
        "Rush+Rec Yds": "RushingYards,ReceivingYards",
        "Sacks": "Sacks",
        "Tackles+Ast": "TackleAssists,Tackles",
        "FG Made": "FieldGoalsMade",
        "Kicking Points": "FieldGoalsMade,FieldGoalsMade,FieldGoalsMade,ExtraPointConversions",
        "Punts": "Punts",
        "Pitcher Strikeouts": "PitcherStrikeouts", 
        "Total Bases": "TotalBases",        
        "Walks Allowed": "WalksAllowed", 
        "Hits Allowed": "HitsAllowed", 
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hits+Runs+RBIS": "HitsAndRunsAndRBIs",
        "Pitching Outs": "PitchingOuts",        
        "Pitcher Fantasy Score": "PitcherFantasyScore", 
        "Hitter Fantasy Score": "HitterFantasyScore", 
        "RBIs": "RBIs", 
        "Runs": "Runs",         
        "Hitter Strikeouts": "HitterStrikeouts",   
        "Earned Runs Allowed": "EarnedRunsAllowed",
        "Goalie Saves": "GoalieSaves",        
        "Time On Ice": "MinutesOnIce", 
        "Points": "Points", 
        "Interceptions": "Interceptions", 
        "Fouls": "Fouls", 
        "Fouls Drawn": "FoulsDrawn", 
        "Shots": "Shots", 
        "Clearances": "Clearances", 
        "Tackles": "Tackles", 
        "Crosses": "Crosses", 
        "Shots Assisted": "ShotsAssisted", 
        "Shots Attempted": "ShotsAttempted",
        "Passes Attempted": "PassesAttempted",
        "Shots On Target": "ShotsOnTarget",
        "Shifts": "Shifts", 
        "Goals": "Goals", 
        "Goals + Assist": "Goals,Assist", 
        "Strokes": "Strokes", 
        "Birdies Or Better": "BirdiesOrBetter", 
        "Shots On Goal": "ShotsOnGoal", 
        "SOG + BS": "ShotsOnGoal,BlockedShots",
        "Assists": "Assists", 
        "Faceoffs Won": "FaceoffsWon", 
        "Hits": "Hits", 
        "Points": "Points",  
        "Rebounds": "Rebounds",        
        "Offensive Rebounds": "OffensiveRebounds",   
        "Defensive Rebounds": "DefensiveRebounds",   
        "Assists": "Assists",       
        "Turnovers": "Turnovers",  
        "Steals": "Steals",      
        "Blocked Shots": "BlockedShots",        
        "FG Attempted": "FieldGoalsAttempted",  
        "FG Made": "FieldGoalsMade",  
        "FG Missed": "FieldGoalsMissed",  
        "3-PT Made": "ThreePointersMade",    
        "3-PT Attempted": "ThreePointersAttempted",         
        "Free Throws Made": "FreeThrowsMade",  
        "Pts+Rebs+Asts": "PtsRebsAsts",               
        "Blks+Stls": "BlksStls",  
        "Pts+Asts": "PtsAsts",   
        "Pts+Rebs": "PtsRebs",   
        "Rebs+Asts": "RebsAsts",  
    }
    return stat_mapping.get(stat_type, None)
