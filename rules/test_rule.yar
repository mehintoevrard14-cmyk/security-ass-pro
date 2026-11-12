
rule ASS_PRO_Test_Detection
{
    meta:
        author = "ASS PRO"
        description = "Regle pedagogique de detection"

    strings:
        $test = "ASS_PRO_MALWARE_TEST"

    condition:
        $test
}

