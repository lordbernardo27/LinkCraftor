<?php

namespace LinkCraftor\Runtime;

final class AdminHooks
{
    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            'admin_init',
            [ self::class, 'onAdminInit' ],
            10,
            0
        );
    }

    public static function onAdminInit(): void
    {
        PluginEvents::dispatch(
            PluginEvents::ADMIN_READY
        );
    }
}