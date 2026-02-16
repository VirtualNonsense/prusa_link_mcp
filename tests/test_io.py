from prusa_mcp.io import FolderEntry, StorageList


def test_folder_entry_top() -> None:
    FolderEntry.model_validate_json(
        '{"type":"FOLDER","ro":false,"name":"usb","children":[{"name":"MANUAL~1","ro":false,"type":"FOLDER","m_timestamp":1641284599,"display_name":"MANUAL_KIT"},{"name":"EXAMPLE","ro":false,"type":"FOLDER","m_timestamp":1645021321,"display_name":"Example"}]}')


def test_folder_entry_example() -> None:
    FolderEntry.model_validate_json(
        '{"type":"FOLDER","ro":false,"m_timestamp":1645021321,"name":"EXAMPLE","children":[{"name":"NUT_15~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1591735639,"refs":{"icon":"/thumb/s/usb/EXAMPLE/NUT_15~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/NUT_15~1.GCO","download":"/usb/EXAMPLE/NUT_15~1.GCO"},"display_name":"Nut_150um_MINI_PLA_1h32m.gcode"},{"name":"PRUSA_~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1581556045,"refs":{"icon":"/thumb/s/usb/EXAMPLE/PRUSA_~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/PRUSA_~1.GCO","download":"/usb/EXAMPLE/PRUSA_~1.GCO"},"display_name":"Prusa_200um_MINI_PLA_23m.gcode"},{"name":"3DBENC~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1641284644,"refs":{"icon":"/thumb/s/usb/EXAMPLE/3DBENC~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/3DBENC~1.GCO","download":"/usb/EXAMPLE/3DBENC~1.GCO"},"display_name":"3DBenchy_PLA_150um_MINI_2h.gcode"},{"name":"BUDDY_~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1581556082,"refs":{"icon":"/thumb/s/usb/EXAMPLE/BUDDY_~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/BUDDY_~1.GCO","download":"/usb/EXAMPLE/BUDDY_~1.GCO"},"display_name":"Buddy_150um_MINI_PLA_2h.gcode"},{"name":"SCREW_~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1591735632,"refs":{"icon":"/thumb/s/usb/EXAMPLE/SCREW_~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/SCREW_~1.GCO","download":"/usb/EXAMPLE/SCREW_~1.GCO"},"display_name":"Screw_150um_MINI_PLA_3h27m.gcode"},{"name":"SHEEP_~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1581556097,"refs":{"icon":"/thumb/s/usb/EXAMPLE/SHEEP_~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/SHEEP_~1.GCO","download":"/usb/EXAMPLE/SHEEP_~1.GCO"},"display_name":"Sheep_pmoews_200um_MINI_PLA_2h17m.gcode"},{"name":"TREEFR~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1581555979,"refs":{"icon":"/thumb/s/usb/EXAMPLE/TREEFR~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/TREEFR~1.GCO","download":"/usb/EXAMPLE/TREEFR~1.GCO"},"display_name":"Treefrog_variable_MINI_PLA_1h15m.gcode"},{"name":"WHISTL~1.GCO","ro":false,"type":"PRINT_FILE","m_timestamp":1591735507,"refs":{"icon":"/thumb/s/usb/EXAMPLE/WHISTL~1.GCO","thumbnail":"/thumb/l/usb/EXAMPLE/WHISTL~1.GCO","download":"/usb/EXAMPLE/WHISTL~1.GCO"},"display_name":"Whistle_200um_MINI_PLA_32m.gcode"}]}')


def test_storage() -> None:
    StorageList.model_validate_json('{"storage_list":[{"path":"/usb/","name":"usb","type":"USB","read_only":false,"available":true}]}')

