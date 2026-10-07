<?php

namespace LinkCraftor\Runtime;

final class WordPressHooks
{
    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            'init',
            [ self::class, 'onInit' ],
            10,
            0
        );
    }

    public static function onInit(): void
    {
        PluginEvents::dispatch(
            PluginEvents::WORDPRESS_READY
        );
    }
}