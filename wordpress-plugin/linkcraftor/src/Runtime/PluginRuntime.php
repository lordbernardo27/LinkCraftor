<?php

namespace LinkCraftor\Runtime;

final class PluginRuntime
{
    private static bool $booted = false;

    private static ?HookRegistry $hooks = null;

    public static function boot(): void
    {
        if ( self::$booted ) {
            return;
        }

        self::$hooks = new HookRegistry();

        WordPressHooks::register( self::$hooks );
        AdminHooks::register( self::$hooks );
        RestHooks::register( self::$hooks );
        ContentHooks::register( self::$hooks );
        EditorHooks::register( self::$hooks );
        SyncHooks::register( self::$hooks );
        AutomationHooks::register( self::$hooks );
        PluginEventHooks::register( self::$hooks );
        Scheduler::register( self::$hooks );

        self::$booted = true;

        PluginEvents::dispatch(
            PluginEvents::RUNTIME_BOOTED
        );
    }

    public static function isBooted(): bool
    {
        return self::$booted;
    }

    public static function registeredHooks(): array
    {
        if ( self::$hooks === null ) {
            return [];
        }

        return self::$hooks->all();
    }
}