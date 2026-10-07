<?php

namespace LinkCraftor\Runtime;

final class AutomationHooks
{
    public const TICK_HOOK = 'linkcraftor_automation_tick';

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
            PluginEvents::AUTOMATION_TICK
        );
    }
}