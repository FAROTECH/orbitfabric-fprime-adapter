"""Live GDS acceptance for the canonical OrbitFabric F Prime projection."""


def test_projected_command_drives_projected_telemetry_and_event(fprime_test_api):
    fprime_test_api.clear_histories()

    fprime_test_api.send_and_assert_command(
        "Ref.pingRcvr.OF_SetMode",
        ["2"],
        max_delay=5,
    )

    fprime_test_api.assert_telemetry(
        "Ref.pingRcvr.OF_Temperature",
        22.0,
        start=0,
        timeout=5,
    )
    fprime_test_api.assert_event(
        "Ref.pingRcvr.OF_ModeChanged",
        start=0,
        timeout=5,
    )
