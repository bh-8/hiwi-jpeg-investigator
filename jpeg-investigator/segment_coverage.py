def determine_gaps(parsing_data_dict: dict) -> list:
    parsed_segments = parsing_data_dict["segments"]
    total_length = parsing_data_dict["parsing_stats"]["data_length"]
    uncovered_gaps = []

    compare_position = 0
    for segment in parsed_segments:
        if segment["position"] != compare_position:
            uncovered_gaps.append((compare_position, segment["position"]))

        compare_position = segment["position"] + segment["payload_length"] + 2

    #check if last segment is not eof yet
    if total_length != compare_position:
        uncovered_gaps.append((compare_position, total_length))
    
    if not len(uncovered_gaps) == 0:
        parsing_data_dict["integrity_errors"]["unidentified_data_found"] = f"File contains unknown data!"

    return uncovered_gaps
