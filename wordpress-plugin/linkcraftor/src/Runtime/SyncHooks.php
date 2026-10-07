<?php

namespace LinkCraftor\Runtime;

final class SyncHooks
{
    public const TICK_HOOK = 'linkcraftor_sync_tick';

    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            self::TICK_HOOK,
            [ self::class, 'onTick' ],
            10,
            0
        );
    }

    public static function onTick(): void
    {
        PluginEvents::dispatch(
            PluginEvents::SYNC_TICK
        );
    }
}