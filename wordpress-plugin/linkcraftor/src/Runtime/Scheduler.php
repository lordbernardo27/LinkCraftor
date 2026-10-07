<?php

namespace LinkCraftor\Runtime;

final class Scheduler
{
    public const FIVE_MINUTES = 'linkcraftor_five_minutes';

    private const ALLOWED_HOOKS = [
        PluginEventHooks::RUNTIME_TICK_HOOK,
        SyncHooks::TICK_HOOK,
        AutomationHooks::TICK_HOOK,
    ];

    public static function register( HookRegistry $hooks ): void
    {
        $hooks->filter(
            'cron_schedules',
            [ self::class, 'addSchedules' ],
            10,
            1
        );
    }

    public static function addSchedules( array $schedules ): array
    {
        if ( ! isset( $schedules[ self::FIVE_MINUTES ] ) ) {
            $schedules[ self::FIVE_MINUTES ] = [
                'interval' => 300,
                'display'  => 'Every Five Minutes',
            ];
        }

        return $schedules;
    }

    public static function scheduleRecurring(
        string $hook,
        string $recurrence = self::FIVE_MINUTES
    ): bool {
        if ( ! in_array( $hook, self::ALLOWED_HOOKS, true ) ) {
            return false;
        }

        if (
            ! function_exists( 'wp_next_scheduled' )
            || ! function_exists( 'wp_schedule_event' )
        ) {
            return false;
        }

        if ( wp_next_scheduled( $hook ) !== false ) {
            return true;
        }

        return false !== wp_schedule_event(
            time() + 300,
            $recurrence,
            $hook
        );
    }

    public static function clear( string $hook ): void
    {
        if (
            in_array( $hook, self::ALLOWED_HOOKS, true )
            && function_exists( 'wp_clear_scheduled_hook' )
        ) {
            wp_clear_scheduled_hook( $hook );
        }
    }

    public static function allowedHooks(): array
    {
        return self::ALLOWED_HOOKS;
    }
}