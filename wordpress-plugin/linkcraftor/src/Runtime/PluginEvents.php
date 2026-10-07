<?php

namespace LinkCraftor\Runtime;

final class PluginEvents
{
    public const RUNTIME_BOOTED = 'linkcraftor/runtime/booted';

    public const WORDPRESS_READY = 'linkcraftor/wordpress/ready';

    public const ADMIN_READY = 'linkcraftor/admin/ready';

    public const REST_READY = 'linkcraftor/rest/ready';

    public const CONTENT_SAVED = 'linkcraftor/content/saved';

    public const CONTENT_UPDATED = 'linkcraftor/content/updated';

    public const EDITOR_READY = 'linkcraftor/editor/ready';

    public const SYNC_TICK = 'linkcraftor/sync/tick';

    public const AUTOMATION_TICK = 'linkcraftor/automation/tick';

    public const RUNTIME_TICK = 'linkcraftor/runtime/tick';

    public static function dispatch(
        string $event,
        mixed ...$arguments
    ): void {
        if ( function_exists( 'do_action' ) ) {
            do_action(
                $event,
                ...$arguments
            );
        }
    }
}