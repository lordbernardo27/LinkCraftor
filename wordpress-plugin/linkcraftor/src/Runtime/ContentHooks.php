<?php

namespace LinkCraftor\Runtime;

final class ContentHooks
{
    public static function register( HookRegistry $hooks ): void
    {
        $hooks->action(
            'save_post',
            [ self::class, 'onSavePost' ],
            10,
            3
        );

        $hooks->action(
            'post_updated',
            [ self::class, 'onPostUpdated' ],
            10,
            3
        );
    }

    public static function onSavePost(
        int $post_id,
        mixed $post,
        bool $update
    ): void {
        PluginEvents::dispatch(
            PluginEvents::CONTENT_SAVED,
            $post_id,
            $post,
            $update
        );
    }

    public static function onPostUpdated(
        int $post_id,
        mixed $post_after,
        mixed $post_before
    ): void {
        PluginEvents::dispatch(
            PluginEvents::CONTENT_UPDATED,
            $post_id,
            $post_after,
            $post_before
        );
    }
}