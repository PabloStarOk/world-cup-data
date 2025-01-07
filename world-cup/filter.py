import os.path as path

import pandas as pd

# ---- Constants ----
# Directories
CURRENT_DIR = path.dirname(path.abspath(__file__))
DATASET_DIRNAME = "data"
MAVEN_DIRNAME = "maven"
EXCEL_DIRNAME = "excel"

# Files
EXCEL_FORMAT = "xlsx"
MATCHES_FILENAME = "world_cup_matches.csv"

# Column Names
HOME_TEAM_COLNAME = "home_team"
AWAY_TEAM_COLNAME = "away_team"
STAGE_COLNAME = "stage"

# ---- Paths ----
# Directories
MATCHES_FILEPATH = path.join(
    CURRENT_DIR, DATASET_DIRNAME, MAVEN_DIRNAME, MATCHES_FILENAME
)

# ---- Data Dictionary ----
OLD_STAGES = [
    ["first_group_stage", 0],
    ["second_group_stage", 1],
    ["first_round", 2],
    ["final_round", 3],
]

MODERN_STAGES = [
    ["group_stage", 4],
    ["round_16", 5],
    ["quarter_finals", 6],
    ["semi_finals", 7],
    ["third_place", 8],
    ["final", 9],
]


class csv_filter:
    def __init__(self, target_national_team: str):
        self.target_national_team = target_national_team.strip().lower()
        self.__read()

    def save_excel(self, output_filename=""):
        if output_filename == "":
            output_filename = "{}-wc-matches".format(self.target_national_team)

        output_filepath = self.__get_out_filepath(
            path.join(CURRENT_DIR, EXCEL_DIRNAME, output_filename)
        )

        try:
            with pd.ExcelWriter(
                output_filepath, engine="auto", mode="w"
            ) as excel_writer:
                self.__save_to_excel(self.stages_df, excel_writer, "Information")
                self.__save_to_excel(
                    self.all_matches,
                    excel_writer,
                    "{} Matches".format(self.target_national_team.capitalize()),
                )
                self.__save_to_excel(self.home_matches, excel_writer, "Home Matches")
                self.__save_to_excel(self.away_matches, excel_writer, "Away Matches")

            print("Saved at: {}".format(output_filepath))
        except ValueError:
            print("Couldn't save to an excel file", ValueError)

    def __get_out_filepath(self, raw_path):
        if not raw_path.endswith(EXCEL_FORMAT):
            paths = raw_path.split(".")

            if len(paths) > 1:
                paths.pop(-1)

            paths.append(EXCEL_FORMAT)

        return ".".join((paths))

    def __read(self):
        # Extract data
        self.matches_df = self.__load_input_file(MATCHES_FILEPATH)

        # Transform data
        self.__transform_data(self.matches_df)
        self.__replace_stages(self.matches_df)

        # Get required data
        self.all_matches, self.home_matches, self.away_matches = self.__filter(
            self.matches_df, self.target_national_team
        )
        self.stages_df = pd.concat(
            [
                pd.DataFrame(OLD_STAGES, columns=["Stage", "Id"]),
                pd.DataFrame(MODERN_STAGES, columns=["Stage", "Id"]),
            ]
        )

    def __load_input_file(self, filepath):
        try:
            print(filepath)
            if not path.exists(filepath):
                print("File path doesn't exist")
                exit()

            df = pd.read_csv(filepath)
            return df
        except ValueError:
            print("Couldn't load file {}".format(ValueError))

    def __save_to_excel(self, df: pd.DataFrame, excel_writer, sheet_name):
        df.to_excel(
            excel_writer=excel_writer,
            sheet_name=sheet_name,
            engine="openpyxl",
            startrow=1,
            startcol=1,
            index=False,
        )

    def __transform_data(self, df) -> pd.DataFrame:
        # Snake case for columns
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Lower case for country names
        df[HOME_TEAM_COLNAME] = df[HOME_TEAM_COLNAME].str.lower()
        df[AWAY_TEAM_COLNAME] = df[AWAY_TEAM_COLNAME].str.lower()

        # Sort values
        df = df.sort_values(by=[HOME_TEAM_COLNAME, AWAY_TEAM_COLNAME], ascending=True)

    def __replace_stages(self, df):
        # Rename stages
        df[STAGE_COLNAME] = (
            df[STAGE_COLNAME]
            .str.strip()
            .str.lower()
            .str.replace(r"\bof\b", "", regex=True)
            .str.replace(r"[-]+", "_", regex=True)
            .str.replace(" ", "_")
            .str.replace(r"_+", "_", regex=True)
        )

        self.__replace_stage_type(df, OLD_STAGES)
        self.__replace_stage_type(df, MODERN_STAGES)

    def __replace_stage_type(self, df: pd.DataFrame, stages: list):
        for stage in stages:
            df[STAGE_COLNAME] = df[STAGE_COLNAME].str.replace(stage[0], str(stage[1]))

    def __filter(self, df, target_team) -> list:
        home_matches = df[df[HOME_TEAM_COLNAME] == target_team]
        away_matches = df[df[AWAY_TEAM_COLNAME] == target_team]
        all_matches = pd.concat([home_matches, away_matches])

        return [all_matches, home_matches, away_matches]
