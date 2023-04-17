<?php
    function compare_timestamps($a, $b) {
        $a_time = strtotime(str_replace('_', ' ', $a));
        $b_time = strtotime(str_replace('_', ' ', $b));

        if ($a_time == $b_time) {
            return 0;
        } else {
            return ($a_time < $b_time) ? -1 : 1;
        }
    }

    function get_latest_file($dir) {
        $files = [];

        if ($dh = opendir($dir)) {
            while (($file = readdir($dh)) !== false) {
                if ($file != '.' && $file != '..' && $file != '.gitignore') {
                    $files[] = str_replace('.json', '', $file);
                }
            }

            closedir($dh);
        }

        usort($files, 'compare_timestamps');

        return $files[count($files) - 1];
    }

    function read_data($file) {
        $json_string = file_get_contents($file);

        if (!$json_string) {
            return [];
        }

        $data = json_decode($json_string, true);

        return $data;
    }

    $file = get_latest_file('files') . '.json';

    $data = read_data('files/' . $file);

    echo json_encode($data);