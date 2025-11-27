try:
    from shadowstream_pb2 import ChangeRecord
    print("import successful")
    cr = ChangeRecord()
    cr.lsn = "123"
    cr.table = "events"
    cr.commit_time = 1732450000000
    print("✅ Instance created:", cr)
except Exception as e:
    print("failed:", e)
    import traceback
    traceback.print_exc()