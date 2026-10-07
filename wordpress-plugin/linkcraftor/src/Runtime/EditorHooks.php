<?php

namespace LinkCraftor\Runtime;

final class EditorHooks
{
    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            'enqueue_block_editor_assets',
            [ self::class, 'onEditorReady' ],
            10,
            0
        );
    }

    public static function onEditorReady(): void
    {
        PluginEvents::dispatch(
            PluginEvents::EDITOR_READY
        );
    }
}