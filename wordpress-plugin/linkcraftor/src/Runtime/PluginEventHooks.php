<?php

namespace LinkCraftor\Runtime;

final class PluginEventHooks
{
    public const RUNTIME_TICK_HOOK = 'linkcraftor_runtime_tick';

    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            self::RUNTIME_TICK_HOOK,
            [ self::class, 'onRuntimeTick' ],
            10,
            0
        );
    }

    public static function onRuntimeTick(): void
    {
        PluginEvents::dispatch(
            PluginEvents::RUNTIME_TICK
        );
    }
}