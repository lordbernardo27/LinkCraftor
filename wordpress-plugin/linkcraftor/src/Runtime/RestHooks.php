<?php

namespace LinkCraftor\Runtime;

final class RestHooks
{
    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            'rest_api_init',
            [ self::class, 'onRestApiInit' ],
            10,
            0
        );
    }

    public static function onRestApiInit(): void
    {
        PluginEvents::dispatch(
            PluginEvents::REST_READY
        );
    }
}