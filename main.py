import os
import re
import logging

log = logging.getLogger()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
REGEX_NUM_VERTICES = re.compile(r"element vertex (?P<num>\d+)")
REGEX_PLY_PROPERTY = re.compile(r"property (\w+) (?P<pname>[a-zA-z]+)")
REGEX_PLY_LIST_PROPERTY = re.compile(r"property list (\w+) (\w+) (?P<pname>[a-zA-z]+)")
DEFAULT_PTS_PROPERTY_VALUE = "255"

def init_logger(logger):
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter("%(asctime)s-%(filename)s:%(lineno)s@%(funcName)s() : %(message)s")
    logger.addHandler(console_handler)

def convert_ply_to_pts(source_file, target_file):

    log.info("Starting..")

    reached_end_of_header = False
    found_num_vertices = False
    ply_properties_map = {
        "x": False,
        "y": False,
        "z": False,
        "r": False,
        "g": False,
        "b": False,
        "nx": False,
        "ny": False,
        "nz": False,
    }
    pts_properties_source_order = {
        "x": -1,
        "y": -1,
        "z": -1,
        "intensity": -1,
        "r": -1,
        "g": -1,
        "b": -1
    }
    pts_properties_target_order = [
        "x", "y", "z", "intensity", "r", "g", "b"
    ]

    source_buffer = open(source_file, "r")

    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    target_buffer = open(target_file, "w")

    property_index = 0

    try:
        # TODO: based on the header, bail out if it's not a ASCII ply
        log.info("Parsing header..")

        line = True
        lines_read = 0
        while line:
            line = source_buffer.readline()
            lines_read += 1
            log.info(line)

            if lines_read > 32:
                break

            # Parse the header -------------------------------------------------
            if not reached_end_of_header:
                num_vertices = REGEX_NUM_VERTICES.match(line)
                if num_vertices:
                    num_vertices = num_vertices.group("num")
                    log.info("Found vertices num: %s", num_vertices)
                    found_num_vertices = True
                    target_buffer.write(num_vertices)
                    target_buffer.write("\n")
                    continue

                # We don't care for List properties
                if REGEX_PLY_LIST_PROPERTY.match(line):
                    continue

                property_description = REGEX_PLY_PROPERTY.match(line)
                if property_description:
                    property_name = property_description.group("pname")
                    try:
                        ply_properties_map[property_name] = True
                    except KeyError:
                        log.error("Non supported PLY property detected: %s",
                                property_name)
                        continue

                    log.info("property name: %s", property_name)
                    if pts_properties_source_order.get(property_name):
                        pts_properties_source_order[property_name] = property_index
                        property_index += 1
                        continue

            if "end_header" not in line:
                continue
            else:
                reached_end_of_header = True
                log.info("Reached end of header, parsing file content..")
                if not found_num_vertices:
                    # TODO: the header is over, but haven't found the
                    # line containing the num of vertices.. bail out!
                    raise RuntimeError("AAAA")

                continue

            # Append the actual values -----------------------------------------
            current_values = [v for v in line.split(" ") if v != "\n"]

            # Read properties using the original ordering
            # but write them in the pts expected order
            # If there PTS properties that we need to fill in but were not
            # not found in our source PLY, we set them to a default value
            for _, pts_prop in enumerate(pts_properties_target_order):
                source_index = pts_properties_source_order.get(pts_prop)
                log.info("source_index: %s", source_index)

                if source_index == -1:
                    target_buffer.write(DEFAULT_PTS_PROPERTY_VALUE)
                    target_buffer.write(" ")
                    continue

                log.info(source_index)
                log.info(current_values)
                prop_value = current_values[source_index]
                target_buffer.write(prop_value)
                target_buffer.write(" ")
            target_buffer.write("\n")
            break

        import pprint
        log.info(pprint.pformat(pts_properties_source_order))
        log.info("Detected PLY properties: %s", sorted([k for k,v in ply_properties_map.items() if v]))
        log.info("Detected PTS properties: %s",
                sorted([k for k,v in ply_properties_map.items()
                if v and k in pts_properties_target_order]))

    finally:
        source_buffer.close()
        target_buffer.close()

def main():
    init_logger(log)
    convert_ply_to_pts(os.path.join(CURRENT_DIR, "..", "geo", "ply", "rocks_1.ply"),
                       os.path.join(CURRENT_DIR, "..", "geo", "pts", "rocks_1.pts"))


if __name__ == '__main__':
    main()
