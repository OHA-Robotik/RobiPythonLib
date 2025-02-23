import rsrc_frame

if __name__ == "__main__":
    frame = rsrc_frame.RSRCFrame(
        msdt=0x1234,
        enabled_feature_set=rsrc_frame.efs.EnabledFeatureSetFrameData(
            enable_poti_state=True,
        ),
        poti_frame_data=rsrc_frame.poti.PotiFrameData(value=int(1000 / 1023 * 255)),
    )

    print(frame.as_bytes())
