from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\runtime\universal_worker\stale.py"
)

text = path.read_text(
    encoding="utf-8"
)


old_import = '''from backend.server.runtime.universal_worker.heartbeat import (
    UniversalWorkerHeartbeat,
    normalize_universal_worker_heartbeat_timestamp,
)
'''


new_import = '''from backend.server.runtime.universal_worker.heartbeat import (
    UniversalWorkerHeartbeat,
    normalize_universal_worker_heartbeat_sequence,
    normalize_universal_worker_heartbeat_timestamp,
)
from backend.server.runtime.universal_worker.registration import (
    normalize_universal_worker_id,
    normalize_universal_worker_instance_id,
    normalize_universal_worker_type,
)
'''


if old_import not in text:
    raise SystemExit(
        "Expected heartbeat import block not found. "
        "Production file was not patched."
    )


text = text.replace(
    old_import,
    new_import,
    1,
)


old_validation = '''        if not isinstance(
            self.worker_id,
            str,
        ) or not self.worker_id:

            raise UniversalStaleWorkerError(
                "Invalid worker_id in stale result.",
                code="invalid_stale_worker_result_worker_id",
                value=self.worker_id,
            )

        if not isinstance(
            self.worker_instance_id,
            str,
        ) or not self.worker_instance_id:

            raise UniversalStaleWorkerError(
                (
                    "Invalid worker_instance_id "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            )

        if not isinstance(
            self.worker_type,
            str,
        ) or not self.worker_type:

            raise UniversalStaleWorkerError(
                "Invalid worker_type in stale result.",
                code="invalid_stale_worker_result_worker_type",
                value=self.worker_type,
            )

        heartbeat_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            )
        )
'''


new_validation = '''        try:

            worker_id = (
                normalize_universal_worker_id(
                    self.worker_id
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                "Invalid worker_id in stale result.",
                code="invalid_stale_worker_result_worker_id",
                value=self.worker_id,
            ) from exc

        try:

            worker_instance_id = (
                normalize_universal_worker_instance_id(
                    self.worker_instance_id
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                (
                    "Invalid worker_instance_id "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "worker_instance_id"
                ),
                value=self.worker_instance_id,
            ) from exc

        try:

            worker_type = (
                normalize_universal_worker_type(
                    self.worker_type
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                "Invalid worker_type in stale result.",
                code="invalid_stale_worker_result_worker_type",
                value=self.worker_type,
            ) from exc

        heartbeat_at = (
            normalize_universal_worker_heartbeat_timestamp(
                self.heartbeat_at
            )
        )
'''


if old_validation not in text:
    raise SystemExit(
        "Expected identity validation block not found. "
        "Production file was not patched."
    )


text = text.replace(
    old_validation,
    new_validation,
    1,
)


old_sequence = '''        if (
            type(self.heartbeat_sequence) is not int
            or
            self.heartbeat_sequence < 1
        ):

            raise UniversalStaleWorkerError(
                (
                    "Invalid heartbeat_sequence "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "heartbeat_sequence"
                ),
                value=self.heartbeat_sequence,
            )
'''


new_sequence = '''        try:

            heartbeat_sequence = (
                normalize_universal_worker_heartbeat_sequence(
                    self.heartbeat_sequence
                )
            )

        except Exception as exc:

            raise UniversalStaleWorkerError(
                (
                    "Invalid heartbeat_sequence "
                    "in stale result."
                ),
                code=(
                    "invalid_stale_worker_result_"
                    "heartbeat_sequence"
                ),
                value=self.heartbeat_sequence,
            ) from exc
'''


if old_sequence not in text:
    raise SystemExit(
        "Expected heartbeat sequence validation block not found. "
        "Production file was not patched."
    )


text = text.replace(
    old_sequence,
    new_sequence,
    1,
)


old_setattrs = '''        object.__setattr__(
            self,
            "heartbeat_at",
            heartbeat_at,
        )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        object.__setattr__(
            self,
            "stale_threshold_seconds",
            threshold,
        )
'''


new_setattrs = '''        object.__setattr__(
            self,
            "worker_id",
            worker_id,
        )

        object.__setattr__(
            self,
            "worker_instance_id",
            worker_instance_id,
        )

        object.__setattr__(
            self,
            "worker_type",
            worker_type,
        )

        object.__setattr__(
            self,
            "heartbeat_at",
            heartbeat_at,
        )

        object.__setattr__(
            self,
            "heartbeat_sequence",
            heartbeat_sequence,
        )

        object.__setattr__(
            self,
            "evaluated_at",
            evaluated_at,
        )

        object.__setattr__(
            self,
            "stale_threshold_seconds",
            threshold,
        )
'''


if old_setattrs not in text:
    raise SystemExit(
        "Expected canonical setattr block not found. "
        "Production file was not patched."
    )


text = text.replace(
    old_setattrs,
    new_setattrs,
    1,
)


path.write_text(
    text,
    encoding="utf-8",
)

print(
    "4.1.11 minimal hardening patch applied."
)
